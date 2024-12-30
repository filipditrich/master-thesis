import subprocess
import re
from datetime import datetime
import json
from pathlib import Path


def get_file_history(file_path):
	"""Get all commits that modified the file."""
	cmd = ['git', 'log', '--follow', '--format=%H|%aI', '--', file_path]
	result = subprocess.run(cmd, capture_output=True, text=True)
	commits = []

	for line in result.stdout.splitlines():
		hash, date = line.split('|')
		commits.append({ 'hash': hash, 'date': date })

	return commits


def get_file_content_at_commit(file_path, commit_hash):
	"""Get file content at specific commit."""
	cmd = ['git', 'show', f'{commit_hash}:{file_path}']
	result = subprocess.run(cmd, capture_output=True, text=True)
	return result.stdout


def get_pdf_link(commit_hash):
	"""Generate PDF link for specific commit."""
	base_url = "https://raw.githubusercontent.com/filipditrich/master-thesis"
	return f"{base_url}/{commit_hash}/thesis/dist/main.pdf"


def extract_stats(content):
	"""Extract progress stats from README content."""
	patterns = {
		'word_count': r'<!-- word-count-start -->(.*?)<!-- word-count-end -->',
		'estimated_pages': r'<!-- estimated-pages-start -->(.*?)<!-- estimated-pages-end -->',
		'actual_pages': r'<!-- actual-pages-start -->(.*?)<!-- actual-pages-end -->',
	}

	stats = { }
	for key, pattern in patterns.items():
		match = re.search(pattern, content)
		if match:
			stats[key] = match.group(1).strip()

	return stats


def main():
	readme_path = 'README.md'
	commits = get_file_history(readme_path)
	historical_data = []

	for commit in commits:
		try:
			content = get_file_content_at_commit(readme_path, commit['hash'])
			stats = extract_stats(content)
			if all(key in stats for key in ['word_count', 'estimated_pages', 'actual_pages']):
				entry = {
					'date': commit['date'],
					'hash': commit['hash'],
					'pdf_link': get_pdf_link(commit['hash']),
					**stats
				}
				historical_data.append(entry)
		except subprocess.CalledProcessError:
			continue

	# Group by day but keep early morning updates (1-6 AM)
	historical_data.sort(key=lambda x: x['date'])  # Sort ascending first
	daily_data = { }
	for entry in historical_data:
		date_obj = datetime.fromisoformat(entry['date'])
		hour = date_obj.hour
		date_day = entry['date'].split('T')[0]

		if 1 <= hour <= 6:  # Keep all early morning updates
			key = f"{date_day}_early_{hour}"
			daily_data[key] = entry
		else:  # For other times, keep last update of the day
			daily_data[date_day] = entry

	# Convert back to list and sort descending
	unique_data = list(daily_data.values())
	unique_data.sort(key=lambda x: x['date'], reverse=True)

	# Generate table rows
	table_rows = ""
	for entry in unique_data:
		date_obj = datetime.fromisoformat(entry['date'])
		formatted_date = date_obj.strftime("%Y-%m-%d %I:%M %p")
		table_rows += f"""        <tr>
            <td>{entry['word_count']}</td>
            <td>{entry['estimated_pages']}</td>
            <td>{entry['actual_pages']}</td>
            <td>{formatted_date}</td>
            <td><a href="{entry['pdf_link']}" target="_blank">👀 View</a></td>
        </tr>
"""

	# Update README
	with open(readme_path, 'r') as f:
		content = f.read()

	# Replace table content
	table_pattern = r'<!-- progress-table-start -->.*?<!-- progress-table-end -->'
	table_html = f"""<!-- progress-table-start -->
    <tbody>
{table_rows}    </tbody>
    <!-- progress-table-end -->"""

	new_content = re.sub(table_pattern, table_html, content, flags=re.DOTALL)

	with open(readme_path, 'w') as f:
		f.write(new_content)


if __name__ == "__main__":
	main()
