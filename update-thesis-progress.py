import re
import sys
from pathlib import Path
import PyPDF2
from datetime import datetime


# Previous functions remain the same until update_readme
def clean_latex_text(text):
	"""Remove LaTeX commands and environments."""
	# Remove comments
	text = re.sub(r'%.*$', '', text, flags=re.MULTILINE)

	# Remove common LaTeX commands
	text = re.sub(r'\\[a-zA-Z]+(?:\[.*?\])?{.*?}', '', text)

	# Remove math environments
	text = re.sub(r'\$.*?\$', '', text)
	text = re.sub(r'\\\[.*?\\\]', '', text)
	text = re.sub(r'\\begin{equation}.*?\\end{equation}', '', text, flags=re.DOTALL)

	# Remove other common environments
	text = re.sub(r'\\begin{.*?}.*?\\end{.*?}', '', text, flags=re.DOTALL)

	# Remove remaining LaTeX commands
	text = re.sub(r'\\[a-zA-Z]+', '', text)

	# Remove curly braces
	text = re.sub(r'{|}', '', text)

	return text


def find_included_files(text, base_path):
	"""Find all \input and \include commands and return the file paths."""
	include_pattern = r'\\(?:input|include){([^}]+)}'
	includes = re.finditer(include_pattern, text)

	files = []
	for match in includes:
		filename = match.group(1)
		if not filename.endswith('.tex'):
			filename += '.tex'

		file_path = Path(base_path) / filename
		if file_path.exists():
			files.append(file_path)
		else:
			print(f"Warning: Included file not found: {file_path}")

	return files


def analyze_latex_document(filepath, processed_files=None):
	"""Analyze a LaTeX document and its included files."""
	if processed_files is None:
		processed_files = set()

	filepath = Path(filepath).resolve()
	if filepath in processed_files:
		return 0

	processed_files.add(filepath)

	try:
		with open(filepath, 'r', encoding='utf-8') as file:
			content = file.read()

		included_files = find_included_files(content, filepath.parent)
		total_words = 0

		cleaned_text = clean_latex_text(content)
		words = [word for word in cleaned_text.split() if word.strip()]
		total_words += len(words)

		for included_file in included_files:
			included_words = analyze_latex_document(included_file, processed_files)
			if isinstance(included_words, int):
				total_words += included_words

		return total_words

	except FileNotFoundError:
		print(f"Error: File '{filepath}' not found.")
		return 0
	except Exception as e:
		print(f"Error analyzing document: {str(e)}")
		return 0


def update_badge(content, progress, color):
	"""Update the thesis progress badge."""
	badge_pattern = r'(<img src="https://img\.shields\.io/badge/Thesis)-[0-9.]+%25-[a-zA-Z]+(")'
	return re.sub(badge_pattern, f'\\1-{progress:.1f}%25-{color}\\2', content)


def extract_table_data(content):
	"""Extract existing table data from README."""
	table_pattern = r'<tbody>\s*<tr>.*?</tr>\s*</tbody>'
	match = re.search(table_pattern, content, re.DOTALL)
	if not match:
		return []

	rows = []
	row_pattern = r'<tr>\s*<td>(.*?)</td>\s*<td>(.*?)</td>\s*<td>(.*?)</td>\s*<td>(.*?)</td>\s*<td>(.*?)</td>\s*</tr>'
	for row_match in re.finditer(row_pattern, match.group(0)):
		groups = [cell.strip() for cell in row_match.groups()]
		rows.append({ 'data': groups[:4], 'link': groups[4] })
	return rows


def update_readme(readme_path, stats):
	"""Update README.md with LaTeX document statistics and progress badge."""
	if not readme_path:
		print(f"No readme file provided, skipping updating...")
		return True

	try:
		with open(readme_path, 'r', encoding='utf-8') as file:
			content = file.read()

		# Calculate progress
		progress = calculate_progress(stats['estimated_pages'])
		progress_color = get_progress_color(progress)

		# Update badge
		content = update_badge(content, progress, progress_color)

		# Find the progress table using markers
		table_start = '<!-- progress-table-start -->'
		table_end = '<!-- progress-table-end -->'
		if table_start not in content or table_end not in content:
			print("Progress table markers not found in README")
			return False

		# Extract existing table data
		table_pattern = f"{table_start}.*?{table_end}"
		table_match = re.search(table_pattern, content, re.DOTALL)
		if not table_match:
			return False

		table_content = table_match.group(0)
		existing_rows = extract_table_data(table_content)

		# Create new row with current stats
		current_time = datetime.now().strftime("%Y-%m-%d %I:%M %p")
		new_row = {
			'data': [
				str(stats['word_count']),
				str(stats['estimated_pages']),
				str(stats['actual_pages']),
				current_time
			],
			'link': '<a href="https://raw.githubusercontent.com/filipditrich/master-thesis/main/thesis/dist/main.pdf" target="_blank">🟢 View</a>'
		}

		# Check if stats have changed from last update
		should_add_row = True
		if existing_rows:
			last_row = existing_rows[0]
			if (last_row['data'][0] == new_row['data'][0] and
					last_row['data'][1] == new_row['data'][1] and
					last_row['data'][2] == new_row['data'][2]):
				should_add_row = False

		# Update rows list
		all_rows = [new_row] + existing_rows if should_add_row else existing_rows

		# Create updated table HTML
		table_rows = ""
		for row in all_rows:
			table_rows += f"""        <tr>
            <td>{row['data'][0]}</td>
            <td>{row['data'][1]}</td>
            <td>{row['data'][2]}</td>
            <td>{row['data'][3]}</td>
            <td>{row['link']}</td>
        </tr>
"""

		# Replace only the progress table content
		table_html = f"{table_start}\n    <tbody>\n{table_rows}    </tbody>\n    {table_end}"
		content = re.sub(table_pattern, table_html, content, flags=re.DOTALL)

		# Update markers for current stats
		markers = {
			'<!-- word-count-start -->': '<!-- word-count-end -->',
			'<!-- estimated-pages-start -->': '<!-- estimated-pages-end -->',
			'<!-- actual-pages-start -->': '<!-- actual-pages-end -->',
			'<!-- last-updated-start -->': '<!-- last-updated-end -->'
		}

		values = {
			'word-count': str(stats['word_count']),
			'estimated-pages': str(stats['estimated_pages']),
			'actual-pages': str(stats['actual_pages']),
			'last-updated': current_time
		}

		# Update each marker
		for key in markers:
			stat_type = key.replace('<!-- ', '').replace('-start -->', '')
			pattern = f"{key}.*?{markers[key]}"
			replacement = f"{key}{values[stat_type]}{markers[key]}"
			content = re.sub(pattern, replacement, content, flags=re.DOTALL)

		# Write updated content
		with open(readme_path, 'w', encoding='utf-8') as file:
			file.write(content)

		return True

	except Exception as e:
		print(f"Error updating README: {str(e)}")
		return False


def calculate_progress(estimated_pages, target_pages=65):
	"""Calculate progress percentage based on estimated pages."""
	progress = (estimated_pages / target_pages) * 100
	return min(100, round(progress, 1))


def get_progress_color(progress):
	"""Return shield.io color based on progress percentage."""
	if progress < 30:
		return 'red'
	elif progress < 60:
		return 'orange'
	elif progress < 90:
		return 'yellow'
	else:
		return 'green'


def get_pdf_page_count(pdf_path):
	"""Get the actual number of pages from the PDF."""
	try:
		with open(pdf_path, 'rb') as file:
			pdf = PyPDF2.PdfReader(file)
			return len(pdf.pages)
	except Exception as e:
		print(f"Error reading PDF: {str(e)}")
		return None


def main():
	if len(sys.argv) < 3:
		print("Usage: python readme_updater.py <tex_file> <pdf_file> <readme_file>")
		return

	tex_path = Path(sys.argv[1])
	pdf_path = Path(sys.argv[2])
	readme_path = Path(sys.argv[3]) if len(sys.argv) > 3 else None

	# Check if files exist
	if not all(p.exists() for p in [tex_path, pdf_path]):
		print("Error: One or more input files do not exist")
		return

	# Analyze LaTeX document
	word_count = analyze_latex_document(tex_path)
	estimated_pages = round(word_count / 250, 1)
	actual_pages = get_pdf_page_count(pdf_path)

	# Prepare stats dictionary
	stats = {
		'word_count': word_count,
		'estimated_pages': estimated_pages,
		'actual_pages': actual_pages
	}

	# Update README
	if update_readme(readme_path, stats):
		progress = calculate_progress(estimated_pages)
		print(f"\nSuccessfully updated {readme_path}")
		print(f"Word count: {word_count}")
		print(f"Estimated pages: {estimated_pages}")
		print(f"Actual pages: {actual_pages}")
		print(f"Progress: {progress}%")
	else:
		print("Failed to update README")


if __name__ == "__main__":
	main()
