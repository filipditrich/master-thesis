from __future__ import annotations

import datetime

import dash_mantine_components as dmc
from dash import dash, dcc, html
from dash_iconify import DashIconify

from dashboard_app._db_utils import QueryDefinition, QueryManager, QueryParameter
from dashboard_app._format_utils import format_number, format_number_short, format_volume, interpolated_text_with_components, parse_date


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
								color="green",
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
						className="with-loading",
						children=[
							dcc.Loading(
								type="dot",
								target_components={ "total-consumption-card": "children" },
								id="total-consumption-card"
							),
						]
					),
					# returnable cups
					dmc.GridCol(
						span=4,
						className="with-loading",
						children=[
							dcc.Loading(
								type="dot",
								target_components={ "returnable-cups-card": "children" },
								id="returnable-cups-card"
							),
						]
					),
					# top category
					dmc.GridCol(
						span=4,
						className="with-loading",
						children=[
							dcc.Loading(
								type="dot",
								target_components={ "top-category-card": "children" },
								id="top-category-card"
							),
						]
					),
					# top beer beverage
					dmc.GridCol(
						span=4,
						className="with-loading",
						children=[
							dcc.Loading(
								type="dot",
								target_components={ "top-beer-card": "children" },
								id="top-beer-card"
							),
						]
					),
					# top other alcohol beverage
					dmc.GridCol(
						span=4,
						className="with-loading",
						children=[
							dcc.Loading(
								type="dot",
								target_components={ "top-other-alcohol-card": "children" },
								id="top-other-alcohol-card"
							),
						]
					),
					# top non-alcoholic beverage
					dmc.GridCol(
						span=4,
						className="with-loading",
						children=[
							dcc.Loading(
								type="dot",
								target_components={ "top-non-alcoholic-card": "children" },
								id="top-non-alcoholic-card"
							),
						]
					),
				]
			)
		],
	)


def beverages_section_callbacks(app):
	# update consumption
	@app.register_callback(
		background=True,
		output=(
				dash.Output("total-consumption-card", "children"),
				dash.Output("returnable-cups-card", "children"),
				dash.Output("top-category-card", "children"),
				dash.Output("top-beer-card", "children"),
				dash.Output("top-other-alcohol-card", "children"),
				dash.Output("top-non-alcoholic-card", "children"),
		),
		inputs=(
				dash.Input("filter-date-from", "value"),
				dash.Input("filter-date-to", "value"),
		),
	)
	async def update_consumption(date_from, date_to):
		results = await app.query_manager.execute_queries(
			query_names=[
				"total_consumption",
				'returnable_cups',
				'category_popularity',
				'beer_brands',
				'non_alcoholic_brands',
				'alcoholic_brands',
			],
			or_query_defs={
				'total_consumption': QueryDefinition(
					name="total_consumption",
					sql=QueryManager.process_sql_query(
						"""
							SELECT * FROM beverage_an_total_consumption(:date_from$1, :date_to$2);
						"""
					),
					parameters=[
						QueryParameter("date_from", datetime.datetime),
						QueryParameter("date_to", datetime.datetime)
					],
					default_data="FSCacheDefault"
				),
				'returnable_cups': QueryDefinition(
					name="returnable_cups",
					sql=QueryManager.process_sql_query(
						"""
							SELECT * FROM beverage_an_returnable_cups(:date_from$1, :date_to$2);
						"""
					),
					parameters=[
						QueryParameter("date_from", datetime.datetime),
						QueryParameter("date_to", datetime.datetime)
					],
					default_data="FSCacheDefault"
				),
				'category_popularity': QueryDefinition(
					name="category_popularity",
					sql=QueryManager.process_sql_query(
						"""
							SELECT * FROM beverage_an_category_popularity(:date_from$1, :date_to$2);
						"""
					),
					parameters=[
						QueryParameter("date_from", datetime.datetime),
						QueryParameter("date_to", datetime.datetime)
					],
					default_data="FSCacheDefault"
				),
				'beer_brands': QueryDefinition(
					name="beer_brands",
					sql=QueryManager.process_sql_query(
						"""
							SELECT * FROM beverage_an_beer_brands(:date_from$1, :date_to$2);
						"""
					),
					parameters=[
						QueryParameter("date_from", datetime.datetime),
						QueryParameter("date_to", datetime.datetime)
					],
					default_data="FSCacheDefault"
				),
				'non_alcoholic_brands': QueryDefinition(
					name="non_alcoholic_brands",
					sql=QueryManager.process_sql_query(
						"""
							SELECT * FROM beverage_an_nonalcoholic_brands(:date_from$1, :date_to$2);
						"""
					),
					parameters=[
						QueryParameter("date_from", datetime.datetime),
						QueryParameter("date_to", datetime.datetime)
					],
					default_data="FSCacheDefault"
				),
				'alcoholic_brands': QueryDefinition(
					name="alcoholic_brands",
					sql=QueryManager.process_sql_query(
						"""
							SELECT * FROM beverage_an_spirits_brands(:date_from$1, :date_to$2);
						"""
					),
					parameters=[
						QueryParameter("date_from", datetime.datetime),
						QueryParameter("date_to", datetime.datetime)
					],
					default_data="FSCacheDefault"
				),
			},
			parameters={
				"date_from": parse_date(date_from),
				"date_to": parse_date(date_to),
			}
		)
		total_consumption_liters = round(results['total_consumption'].iloc[0].get("total_consumption_liters", 0))
		returnable_cups_res = results['returnable_cups'].iloc[0]
		most_popular_category_res = results['category_popularity'].iloc[0]
		beer_brands_res = results['beer_brands']
		top_beer_brand_res = beer_brands_res.iloc[0]
		non_alcoholic_brands_res = results['non_alcoholic_brands']
		top_non_alcoholic_brand_res = non_alcoholic_brands_res.iloc[0]
		alcoholic_brands_res = results['alcoholic_brands']
		top_alcoholic_brand_res = alcoholic_brands_res.iloc[0]

		return [
			# total consumption
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
										children=format_volume(total_consumption_liters * 1000),
										size="xl",
										fw=700
									),
									dmc.ThemeIcon(
										size="lg",
										radius="xl",
										color="green",
										variant="light",
										children=DashIconify(icon="mdi:drink", width=20)
									),
								]
							),
							dmc.Text(
								interpolated_text_with_components(
									"that is roughly equivalent to {hot_tubs} (the average size of a hot tub is about 719 liters)",
									{
										'hot_tubs': dmc.Text(format_number_short(round(total_consumption_liters / 719)) + " hot tubs", fw=700, span=True),
									}
								),
								size="sm",
								className="mt-auto",
								c="dimmed"
							),
						]
					)
				]
			),
			# returnable cups
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
										f"{format_number(returnable_cups_res.get('issued_count', 0))} cups",
										size="xl",
										fw=700
									),
									dmc.ThemeIcon(
										size="lg",
										radius="xl",
										color="green",
										variant="light",
										children=DashIconify(icon="mdi:cup-outline", width=20)
									),
								]
							),
							dmc.Text(
								interpolated_text_with_components(
									"were issued to customers and only {returned_cups} of them have been returned, remaining {not_returned_cups} cups were not returned",
									{
										'returned_cups': dmc.Text(format_number_short(abs(returnable_cups_res.get('returned_count', 0))), fw=700, span=True),
										'not_returned_cups': dmc.Text(format_number_short(returnable_cups_res.get('not_returned_count', 0)), fw=700, span=True)
									}
								),
								size="sm",
								c="dimmed"
							),
							dmc.ProgressRoot(
								[
									dmc.ProgressSection(dmc.ProgressLabel("Returned"), value=abs(returnable_cups_res.get('returned_count', 0)) / returnable_cups_res.get('issued_count', 0) * 100, color="green"),
									dmc.ProgressSection(dmc.ProgressLabel("Not returned"), value=returnable_cups_res.get('not_returned_count', 0) / returnable_cups_res.get('issued_count', 0) * 100, color="gray"),
								],
								size="xl",
							)
						]
					)
				]
			),
			# top category
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
							dmc.SemiCircleProgress(value=most_popular_category_res.get('total_consumption_liters', 0) / total_consumption_liters * 100, label=dmc.Text("Beer", size="xl", fw=700), className="my-auto", size=150, ),
							dmc.Text(
								interpolated_text_with_components(
									"was the most consumed category of {volume}",
									{
										'volume': dmc.Text(format_volume(most_popular_category_res.get('total_consumption_liters', 0) * 1000), fw=700, span=True),
									}
								),
								size="sm",
								c="dimmed"
							),
						]
					)
				]
			),
			# top beer brand
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
										top_beer_brand_res.get('subcategory', 'N/A'),
										size="xl",
										fw=700
									),
									dmc.ThemeIcon(
										size="lg",
										radius="xl",
										color="green",
										variant="light",
										children=DashIconify(icon="ion:beer", width=20)
									),
								]
							),
							dmc.Text(
								interpolated_text_with_components(
									"was the most consumed beer with {volume} drank and {sales} beers sold",
									{
										'volume': dmc.Text(format_volume(top_beer_brand_res.get('total_consumption_liters', 0) * 1000), fw=700, span=True),
										'sales': dmc.Text(format_number(top_beer_brand_res.get('total_sold', 0)), fw=700, span=True),
									}
								),
								size="sm",
							),
							dmc.ProgressRoot(
								[
									dmc.ProgressSection(dmc.ProgressLabel(top_beer_brand_res.get('subcategory', 'N/A')), value=top_beer_brand_res.get('total_consumption_liters', 0) / beer_brands_res['total_consumption_liters'].sum() * 100, color="green"),
									dmc.ProgressSection(
										dmc.ProgressLabel("Other"), value=(beer_brands_res['total_consumption_liters'].sum() - top_beer_brand_res.get('total_consumption_liters', 0)) / beer_brands_res['total_consumption_liters'].sum() * 100, color="gray"
									),
								],
								size="xl",
							),

						]
					)
				]
			),
			# top other alcohol brand
			dmc.Card(
				className="h-full",
				p="sm",
				withBorder=True,
				children=[
					dmc.Stack(
						gap="xs",
						className="grow",
						children=[
							dmc.Text("Alcohol beverages", size="sm", fw=500),
							dmc.Group(
								gap="xs",
								justify="space-between",
								children=[
									dmc.Text(
										top_alcoholic_brand_res.get('subcategory', 'N/A'),
										size="xl",
										fw=700
									),
									dmc.ThemeIcon(
										size="lg",
										radius="xl",
										color="green",
										variant="light",
										children=DashIconify(icon="hugeicons:drink", width=20)
									),
								]
							),
							dmc.Text(
								interpolated_text_with_components(
									"was the most consumed alcohol drink with {volume} drank and {sales} beers sold",
									{
										'volume': dmc.Text(format_volume(top_alcoholic_brand_res.get('total_consumption_liters', 0) * 1000), fw=700, span=True),
										'sales': dmc.Text(format_number(top_alcoholic_brand_res.get('total_sold', 0)), fw=700, span=True),
									}
								),
								size="sm",
							),
							dmc.ProgressRoot(
								[
									dmc.ProgressSection(
										dmc.ProgressLabel(top_alcoholic_brand_res.get('subcategory', 'N/A')), value=top_alcoholic_brand_res.get('total_consumption_liters', 0) / alcoholic_brands_res['total_consumption_liters'].sum() * 100, color="green"
									),
									dmc.ProgressSection(
										dmc.ProgressLabel("Other"), value=(alcoholic_brands_res['total_consumption_liters'].sum() - top_alcoholic_brand_res.get('total_consumption_liters', 0)) / alcoholic_brands_res['total_consumption_liters'].sum() * 100,
										color="gray"
									),
								],
								size="xl",
							),

						]
					)
				]
			),
			# top non-alcoholic brand
			dmc.Card(
				className="h-full",
				p="sm",
				withBorder=True,
				children=[
					dmc.Stack(
						gap="xs",
						className="grow",
						children=[
							dmc.Text("Non-alcohol beverages", size="sm", fw=500),
							dmc.Group(
								gap="xs",
								justify="space-between",
								children=[
									dmc.Text(
										top_non_alcoholic_brand_res.get('subcategory', 'N/A'),
										size="xl",
										fw=700
									),
									dmc.ThemeIcon(
										size="lg",
										radius="xl",
										color="green",
										variant="light",
										children=DashIconify(icon="ion:beer", width=20)
									),
								]
							),
							dmc.Text(
								interpolated_text_with_components(
									"was the most consumed non-alcohol drink with {volume} drank and {sales} beers sold",
									{
										'volume': dmc.Text(format_volume(top_non_alcoholic_brand_res.get('total_consumption_liters', 0) * 1000), fw=700, span=True),
										'sales': dmc.Text(format_number(top_non_alcoholic_brand_res.get('total_sold', 0)), fw=700, span=True),
									}
								),
								size="sm",
							),
							dmc.ProgressRoot(
								[
									dmc.ProgressSection(
										dmc.ProgressLabel(top_non_alcoholic_brand_res.get('subcategory', 'N/A')), value=top_non_alcoholic_brand_res.get('total_consumption_liters', 0) / non_alcoholic_brands_res['total_consumption_liters'].sum() * 100,
										color="green"
									),
									dmc.ProgressSection(
										dmc.ProgressLabel("Other"),
										value=(non_alcoholic_brands_res['total_consumption_liters'].sum() - top_non_alcoholic_brand_res.get('total_consumption_liters', 0)) / non_alcoholic_brands_res['total_consumption_liters'].sum() * 100, color="gray"
									),
								],
								size="xl",
							),
						]
					)
				]
			),
		]
