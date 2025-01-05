from __future__ import annotations

import dash_mantine_components as dmc
from dash import html
from dash_iconify import DashIconify


def customers_section_children(app):
	return html.Section(
		className="flex flex-col bg-white rounded-lg border border-zinc-200",
		children=[
			# Header
			html.Div(
				className="p-4",
				children=[
					html.Div(
						className="flex items-center gap-4",
						children=[
							dmc.ThemeIcon(
								size="xl",
								radius="xl",
								color="red",
								variant="light",
								children=DashIconify(icon="ix:customer-filled", width=25)
							),
							html.Div(
								children=[
									dmc.Title(
										size="1.25rem",
										children='Customer analysis'
									),
									dmc.Text(
										"Insights into customer purchasing patterns and product combinations.",
										c="dimmed",
									),
								]
							)
						],
					),
				]
			),
			# Content
			dmc.Grid(
				gutter="md",
				p="md",
				grow=True,
				children=[
					dmc.GridCol(
						span=12,
						children=dmc.Group(
							gap="md",
							children=[
								"TODO"
							]
						)
					),
				]
			)
		],
	)


def customers_section_callbacks(app):
	pass
