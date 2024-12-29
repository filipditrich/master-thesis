from __future__ import annotations

import dash_mantine_components as dmc
from dash import html
from dash_iconify import DashIconify

from dashboard_app._format_utils import format_number, format_number_short, format_volume, interpolated_text_with_components


def beverages_section_children(app):
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
								children=DashIconify(icon="ion:beer", width=25)
							),
							html.Div(
								children=[
									dmc.Title(
										size="1.25rem",
										children='Beverage consumption analysis'
									),
									dmc.Text(
										"Delve into the beverage consumption data and insights from the event.",
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
					# total consumption
					dmc.GridCol(
						span=4,
						children=[
							dmc.Card(
								className="h-full",
								p="sm",
								withBorder=True,
								children=[
									dmc.Stack(
										gap="xs",
										className="grow",
										children=[
											dmc.Text("Total beverage consumption", size="sm", fw=500),
											dmc.Group(
												gap="xs",
												justify="space-between",
												children=[
													dmc.Text(
														format_volume(
															29343000
														),
														size="xl",
														fw=700
													),
													dmc.ThemeIcon(
														size="lg",
														radius="xl",
														color="red",
														variant="light",
														children=DashIconify(icon="mdi:drink", width=20)
													),
												]
											),
											dmc.Text(
												interpolated_text_with_components(
													"that is roughly equivalent to {hot_tubs} of beverage that has been consumed",
													{
														'hot_tubs': dmc.Text(format_number_short(12) + " hot tubs", fw=700, span=True),
													}
												),
												size="sm",
												className="mt-auto",
												c="dimmed"
											),
										]
									)
								]
							)
						]
					),
					# returnable cups
					dmc.GridCol(
						span=4,
						children=[
							dmc.Card(
								className="h-full",
								p="sm",
								withBorder=True,
								children=[
									dmc.Stack(
										gap="xs",
										className="grow",
										children=[
											dmc.Text("Returnable cups", size="sm", fw=500),
											dmc.Group(
												gap="xs",
												justify="space-between",
												children=[
													dmc.Text(
														f"{format_number(22045)} cups",
														size="xl",
														fw=700
													),
													dmc.ThemeIcon(
														size="lg",
														radius="xl",
														color="red",
														variant="light",
														children=DashIconify(icon="mdi:cup-outline", width=20)
													),
												]
											),
											dmc.Text(
												interpolated_text_with_components(
													"were issued to customers and only {returned_cups} of them have been returned, remaining {not_returned_cups} cups were not returned",
													{
														'returned_cups': dmc.Text(format_number_short(17322), fw=700, span=True),
														'not_returned_cups': dmc.Text(format_number_short(4723), fw=700, span=True)
													}
												),
												size="sm",
												c="dimmed"
											),
											dmc.ProgressRoot(
												[
													dmc.ProgressSection(dmc.ProgressLabel("Returned"), value=17322 / 22045 * 100, color="green"),
													dmc.ProgressSection(dmc.ProgressLabel("Not returned"), value=4723 / 22045 * 100, color="gray"),
												],
												size="xl",
											)
										]
									)
								]
							)
						]
					),
					# top category
					dmc.GridCol(
						span=4,
						children=[
							dmc.Card(
								className="h-full",
								p="sm",
								withBorder=True,
								children=[
									dmc.Stack(
										gap="xs",
										className="grow",
										children=[
											dmc.Text("Top beverage category", size="sm", fw=500),
											dmc.SemiCircleProgress(value=53990 / 106605 * 100, label=dmc.Text("Beer", size="xl", fw=700), className="my-auto", size=150),
											dmc.Text(
												interpolated_text_with_components(
													"was the most consumed category of {volume}",
													{
														'volume': dmc.Text(format_volume(19797000), fw=700, span=True),
													}
												),
												size="sm",
												c="dimmed"
											),
										]
									)
								]
							)
						]
					),
					# top beer beverage
					dmc.GridCol(
						span=4,
						children=[
							dmc.Card(
								className="h-full",
								p="sm",
								withBorder=True,
								children=[
									dmc.Stack(
										gap="xs",
										className="grow",
										children=[
											dmc.Text("Beer beverages", size="sm", fw=500),
											dmc.Group(
												gap="xs",
												justify="space-between",
												children=[
													dmc.Text(
														"Radegast",
														size="xl",
														fw=700
													),
													dmc.ThemeIcon(
														size="lg",
														radius="xl",
														color="red",
														variant="light",
														children=DashIconify(icon="ion:beer", width=20)
													),
												]
											),
											dmc.Text(
												interpolated_text_with_components(
													"was the most consumed beer with {volume} drank and {sales} beers sold",
													{
														'volume': dmc.Text(format_volume(10925000), fw=700, span=True),
														'sales': dmc.Text(format_number(20732), fw=700, span=True),
													}
												),
												size="sm",
											),
											dmc.ProgressRoot(
												[
													dmc.ProgressSection(dmc.ProgressLabel("Radegast"), value=27329 / 53990 * 100, color="green"),
													dmc.ProgressSection(dmc.ProgressLabel("Pilsner Urquell"), value=14137 / 53990 * 100, color="blue"),
													dmc.ProgressSection(dmc.ProgressLabel("Other"), value=12524 / 53990 * 100, color="gray"),
												],
												size="xl",
											),

										]
									)
								]
							)
						]
					),
					# top other alcohol beverage
					dmc.GridCol(
						span=4,
						children=[
							dmc.Card(
								className="h-full",
								p="sm",
								withBorder=True,
								children=[
									dmc.Stack(
										gap="xs",
										className="grow",
										children=[
											dmc.Text("Alcoholic beverages", size="sm", fw=500),
											dmc.Group(
												gap="xs",
												justify="space-between",
												children=[
													dmc.Text(
														"Absolut Vodka",
														size="xl",
														fw=700
													),
													dmc.ThemeIcon(
														size="lg",
														radius="xl",
														color="red",
														variant="light",
														children=DashIconify(icon="nimbus:shot", width=20)
													),
												]
											),
											dmc.Text(
												interpolated_text_with_components(
													"was the most consumed alcoholic drink with {volume} drank and {sales} drinks sold",
													{
														'volume': dmc.Text(format_volume(335080), fw=700, span=True),
														'sales': dmc.Text(format_number(9177), fw=700, span=True),
													}
												),
												size="sm",
											),
											dmc.ProgressRoot(
												[
													dmc.ProgressSection(dmc.ProgressLabel("Absolut Vodka"), value=9177 / 31997 * 100, color="green"),
													dmc.ProgressSection(dmc.ProgressLabel("Beefeater"), value=4628 / 31997 * 100, color="blue"),
													dmc.ProgressSection(dmc.ProgressLabel("Other"), value=22951 / 31997 * 100, color="gray"),
												],
												size="xl",
											),
										]
									)
								]
							)
						]
					),
					# top non-alcoholic beverage
					dmc.GridCol(
						span=4,
						children=[
							dmc.Card(
								className="h-full",
								p="sm",
								withBorder=True,
								children=[
									dmc.Stack(
										gap="xs",
										className="grow",
										children=[
											dmc.Text("Non-alcoholic beverages", size="sm", fw=500),
											dmc.Group(
												gap="xs",
												justify="space-between",
												children=[
													dmc.Text(
														"Birell",
														size="xl",
														fw=700
													),
													dmc.ThemeIcon(
														size="lg",
														radius="xl",
														color="red",
														variant="light",
														children=DashIconify(icon="lucide:beer-off", width=20)
													),
												]
											),
											dmc.Text(
												interpolated_text_with_components(
													"was the most consumed non-alcoholic beverage with {volume} drank and {sales} units sold",
													{
														'volume': dmc.Text(format_volume(21865000), fw=700, span=True),
														'sales': dmc.Text(format_number(4893), fw=700, span=True),
													}
												),
												size="sm",
											),
											dmc.ProgressRoot(
												[
													dmc.ProgressSection(dmc.ProgressLabel("Birell"), value=4893 / 20487 * 100, color="green"),
													dmc.ProgressSection(dmc.ProgressLabel("ZON Lemonade"), value=4508 / 20487 * 100, color="blue"),
													dmc.ProgressSection(dmc.ProgressLabel("Other"), value=11086 / 20487 * 100, color="gray"),
												],
												size="xl",
											),
										]
									)
								]
							)
						]
					),
				]
			)
		],
	)


def beverages_section_callbacks(app):
	# TODO
	pass
