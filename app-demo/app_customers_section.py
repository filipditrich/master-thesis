from __future__ import annotations

import dash_mantine_components as dmc
from dash import html
from dash_iconify import DashIconify


def customers_section_children(app):
	return html.Section(
		className="flex flex-col bg-white rounded-lg border border-zinc-200",
		children=[
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
										"Insights into customer data and behavior during the event.",
										c="dimmed",
									),
								]
							)
						],
					),
				]
			),
			# content
			dmc.Grid(
				gutter="md",
				p="md",
				grow=False,
				children=[
					# TODO
					dmc.GridCol(span=12, children=dmc.Card("TODO", withBorder=True, className="bg-zinc-50"))
				]
			)
		],
	)


def customers_section_callbacks(app):
	pass
