from __future__ import annotations

from typing import Optional

import dateutil
import pandas as pd
from dash import html


def format_number(num: int | float, floating_points: Optional[int] = 0) -> str:
	"""Default number formatter with space as a thousand separator"""
	try:
		if floating_points is not None:
			return f"{num:,.{floating_points}f}".replace(",", " ")
		else:
			return "{:,}".format(num).replace(",", " ")
	except TypeError as e:
		return "-"


locale_cs_d3 = """
d3.formatLocale({
    "decimal": ",",
    "thousands": " ",
    "grouping": [3],
    "currency": ["", " CZK"],
    "nan": "",
})
"""


def parse_date(date: str) -> pd.Timestamp:
	"""Parses date string to pandas Timestamp"""
	try:
		return dateutil.parser.parse(date)
	except ValueError:
		return pd.Timestamp("1970-01-01")


def interpolated_text_with_components(text: str, components: dict):
	"""
	Input: Text with interpolation keys and components mapping
	Returns: Dash component list with interpolated text
	"""
	# Split the text into parts
	parts = text.split("{")

	# Initialize the component list
	component_list = []

	# Iterate over the parts
	for part in parts:
		# Check if the part contains the closing bracket
		if "}" in part:
			# Split the part into key and text
			key, text = part.split("}", 1)

			# Check if the key is in the components
			if key in components:
				# Add the component to the list
				component_list.append(components[key])
			else:
				# Add the text to the list
				component_list.append(html.Span(key))

			# Add the text to the list
			component_list.append(html.Span(text))
		else:
			# Add the text to the list
			component_list.append(html.Span(part))

	return component_list


def format_volume(num: int | float, float_places: int = 0) -> str:
	"""Default volume (ml) formatter with space as thousands separator and 'liters' suffix"""
	try:
		if num >= 1_000:
			return f"{num / 1_000:,.{float_places}f} litres".replace(",", " ")
		else:
			return "{:,}".format(num).replace(",", " ") + " ml"
	except TypeError:
		return "0 litres"


def format_duration(mins: int | float) -> str:
	"""Default duration formatter with hours, minutes and seconds"""
	try:
		hours = int(mins // 60)
		minutes = int(mins % 60)
		seconds = int((mins % 1) * 60)
		if hours > 0:
			return f"{hours} h {minutes} min"
		elif minutes > 0 and seconds > 0:
			return f"{minutes} min {seconds} s"
		elif minutes > 0:
			return f"{minutes} min"
		elif seconds > 0:
			return f"{seconds} s"
		else:
			return "0 min"

	except TypeError:
		return "0 min"


def format_percent(num: int | float) -> str:
	"""Default percent formatter with 1 decimal place"""
	try:
		return f"{num:.1f} %"
	except TypeError:
		return "0.0%"


def format_date(date: str, with_time: Optional[bool] = False) -> str:
	"""Default localized (CZ) date formatter"""
	try:
		if with_time:
			return pd.to_datetime(date).strftime("%d.%m. %H:%M")
		else:
			return pd.to_datetime(date).strftime("%d.%m.")
	except TypeError:
		return "Unknown date"


def format_number_short(num: int | float) -> str:
	"""Formats number to a short form with K suffix for thousands or ..."""
	num = round(num)
	try:
		if num >= 1_000_000:
			should_float = num % 1_000_000 != 0
			if should_float:
				return f"{num / 1_000_000:.1f}M"
			return f"{num / 1_000_000:.0f}M"
		elif num >= 1_000:
			should_float = num % 1_000 != 0
			if should_float:
				return f"{num / 1_000:.1f}K"
			return f"{num / 1_000:.0f}K"
		else:
			return str(num)
	except TypeError:
		return "0"


def format_price(num: int | float) -> str:
	"""Default price formatter with space as a thousand separator and 'CZK' suffix"""
	try:
		return format_number(round(num / 100)) + " CZK"
	except TypeError:
		return "0 CZK"


def format_price_short(num: int | float) -> str:
	"""Formats price to a short form with K suffix for thousands or ..."""
	num = round(num / 100)
	try:
		if num >= 1_000_000:
			should_float = num % 1_000_000 != 0
			if should_float:
				return f"{num / 1_000_000:.1f}M CZK"
			return f"{num / 1_000_000:.0f}M CZK"
		elif num >= 1_000:
			should_float = num % 1_000 != 0
			if should_float:
				return f"{num / 1_000:.1f}K CZK"
			return f"{num / 1_000:.0f}K CZK"
		else:
			return str(num) + " CZK"
	except TypeError:
		return "0 CZK"
