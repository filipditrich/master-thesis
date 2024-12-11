from __future__ import annotations

import asyncio
import json

import dash as dash
import dash_mantine_components as dmc
import dateutil as dateutil
import pandas as pd
import plotly.graph_objects as go
from dash import dcc, html
from dash_iconify import DashIconify
from app_performance_section import performance_section_children, performance_section_callbacks
from app_cashflow_section import cashflow_section_children, cashflow_section_callbacks

from chart_utils import SankeyDiagram
from dash_utils import background_callback_manager, create_cache_key, external_script, index_string
from db_queries import query_manager
from db_utils import format_date, format_number, format_number_short, format_percent, format_price, format_price_short, format_volume, interpolated_text_with_components

# set the React version
dash._dash_renderer._set_react_version("18.2.0")

# (day starts at 06:00am, day ends 05:59am +1 next day)
days = {
	'1': ('2024-07-04 06:00:00', '2024-07-05 05:59:59'),
	'2': ('2024-07-05 06:00:00', '2024-07-06 05:59:59'),
	'3': ('2024-07-06 06:00:00', '2024-07-07 05:59:59'),
	'up-to-1': ('2024-07-04 06:00:00', '2024-07-05 05:59:59'),
	'up-to-2': ('2024-07-04 06:00:00', '2024-07-06 05:59:59'),
	'up-to-3': ('2024-07-04 06:00:00', '2024-07-07 05:59:59'),
}


def fast_preview_playground():
	return []


# ---- Dash Application ----
class MainApplication:
	def __init__(self):
		self._callbacks_registered = False

		self.__app = dash.Dash(
			name=__name__,
			update_title="🔄 Reloading...",
			external_stylesheets=[dmc.styles.ALL, dmc.styles.DATES, dmc.styles.CHARTS],
			external_scripts=external_script,
			background_callback_manager=background_callback_manager,
			index_string=index_string,
		)
		self.__app.enable_async_callbacks = True

		# Set the app layout
		self.__app.layout = self._create_layout()

		# Query manager
		self.query_manager = query_manager

		# FIXME: Register callbacks
		self._register_callbacks()

	def register_callback(self, output, inputs, prevent_initial_call=False, background=False, *args, **kwargs):
		"""
		Decorator for Dash callbacks that handles async operations and error handling.

		Args:
				output: Dash Output or tuple of Outputs
				inputs: Dash Input or tuple of Inputs
				prevent_initial_call: Boolean to prevent initial callback
				background: Boolean to run callback in background
		"""

		def decorator(func):
			# print(f"Registering callback for function {func.__name__}, Output: {output}")

			def async_callback_wrapper(_self, *args, **kwargs):
				"""Async callback wrapper implementation"""

				async def async_function():
					try:
						# TODO: parse args logic?
						parsed_args = args

						# Call the original function with parsed arguments
						return await func(_self, *parsed_args, **kwargs)
					except Exception as e:
						print(f"Error in callback {func.__name__}: {str(e)}")
						raise dash.exceptions.PreventUpdate

				try:
					loop = asyncio.new_event_loop()
					asyncio.set_event_loop(loop)
					return loop.run_until_complete(async_function())
				finally:
					loop.close()

			def sync_callback_wrapper(_self, *args, **kwargs):
				"""Sync callback wrapper implementation"""
				try:
					# TODO: parse args logic?
					parsed_args = args

					# Call the original function with parsed arguments
					return func(_self, *parsed_args, **kwargs)

				except Exception as e:
					print(f"Error in callback {func.__name__}: {str(e)}")
					raise dash.exceptions.PreventUpdate

			# Register the callback with Dash
			if background:
				return self.__app.callback(
					output=output,
					inputs=inputs,
					background=True,
					prevent_initial_call=prevent_initial_call,
					manager=create_cache_key(func.__name__),
					*args, **kwargs
				)(async_callback_wrapper)
			else:
				return self.__app.callback(
					output=output,
					inputs=inputs,
					prevent_initial_call=prevent_initial_call,
					*args, **kwargs
				)(sync_callback_wrapper)

		return decorator

	def _create_layout(self):
		return dmc.MantineProvider(
			html.Div(
				className="grow",
				children=[
					dmc.Container(
						className="grid grid-cols-1 gap-8 py-8 pb-[250px]",
						size="xl",
						children=[
							# Header section
							html.Header(
								children=[
									html.H1(
										className="text-center text-3xl font-bold mb-3",
										children='Event Dashboard'
									),
									html.P(
										className="text-center text-lg font-normal text-gray-500",
										children='Multi-purpose Analytical Dashboard of NFCtron event data'
									),
								]
							),
							# TODO: Filter bar
							html.Div(
								className="flex items-center justify-center gap-4",
								children=[
									dmc.DateTimePicker(
										id="filter-date-from",
										label="Filter from",
										value="2024-07-04T00:00:00",
										w=250,
									),
									dmc.DateTimePicker(
										id="filter-date-to",
										label="Filter to",
										value="2024-07-07T23:59:59",
										w=250,
									),
									dmc.Select(
										label="Select date",
										id="filter-date-preset",
										allowDeselect=False,
										value="all",
										data=[
											{ "value": "1", "label": "Day 1" },
											{ "value": "2", "label": "Day 2" },
											{ "value": "3", "label": "Day 3" },
											{ "value": "up-to-1", "label": "Up to Day 1" },
											{ "value": "up-to-2", "label": "Up to Day 2" },
											{ "value": "up-to-3", "label": "Up to Day 3" },
											{ "value": "all", "label": "Whole festival" },
										],
										w=200,
									),
								]
							),
							# FIXME
							fast_preview_playground(),
							# Main content
							html.Main(
								className="grid grid-cols-1 gap-4",
								children=[
									# TODO: Cashflow and Revenue Analysis
									# cashflow_section_children(self),
									# TODO: Performance Analysis
									performance_section_children(self),
									# TODO: Beverage Consumption analysis
									html.Section(
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
																						'hot_tubs': dmc.Text(format_number_short(12), fw=700, span=True),
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
													# depositable cups
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
																			dmc.Text("Depositable cups", size="sm", fw=500),
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
																			dmc.Divider(className="my-1"),
																			dmc.SimpleGrid(
																				cols=2,
																				spacing="xs",
																				className="grow",
																				children=[
																					dmc.Stack(
																						gap="xs",
																						className="bg-zinc-50 p-2 border border-zinc-200 rounded-sm",
																						children=[
																							dmc.Text("Beers per customer", size="xs"),
																							dmc.Text(
																								f"{format_number(4)} beers",
																								size="md",
																								fw=600
																							)
																						]
																					),
																					dmc.Stack(
																						gap="xs",
																						className="bg-zinc-50 p-2 border border-zinc-200 rounded-sm",
																						children=[
																							dmc.Text("Max consumed", size="xs"),
																							dmc.Text(
																								f"{format_number(48)} beers",
																								size="md",
																								fw=600
																							)
																						]
																					),
																				]
																			)
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
																			dmc.Divider(className="my-1"),
																			dmc.SimpleGrid(
																				cols=2,
																				spacing="xs",
																				className="grow",
																				children=[
																					dmc.Stack(
																						gap="xs",
																						className="bg-zinc-50 p-2 border border-zinc-200 rounded-sm",
																						children=[
																							dmc.Text("Drinks per customer", size="xs"),
																							dmc.Text(
																								f"{format_number(3)} drinks",
																								size="md",
																								fw=600
																							)
																						]
																					),
																					dmc.Stack(
																						gap="xs",
																						className="bg-zinc-50 p-2 border border-zinc-200 rounded-sm",
																						children=[
																							dmc.Text("Max consumed", size="xs"),
																							dmc.Text(
																								f"{format_number(96)} drinks",
																								size="md",
																								fw=600
																							)
																						]
																					),
																				]
																			)
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
																			dmc.Divider(className="my-1"),
																			dmc.SimpleGrid(
																				cols=2,
																				spacing="xs",
																				className="grow",
																				children=[
																					dmc.Stack(
																						gap="xs",
																						className="bg-zinc-50 p-2 border border-zinc-200 rounded-sm",
																						children=[
																							dmc.Text("Beverages per customer", size="xs"),
																							dmc.Text(
																								f"{format_number(2)} drinks",
																								size="md",
																								fw=600
																							)
																						]
																					),
																					dmc.Stack(
																						gap="xs",
																						className="bg-zinc-50 p-2 border border-zinc-200 rounded-sm",
																						children=[
																							dmc.Text("Max consumed", size="xs"),
																							dmc.Text(
																								f"{format_number(16)} drinks",
																								size="md",
																								fw=600
																							)
																						]
																					),
																				]
																			)
																		]
																	)
																]
															)
														]
													),
												]
											)
										],
									),
									# TODO: Customer Analysis
									html.Section(
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
									),
								]
							),
							# TODO: Footer
							html.Footer(
								children=[]
							)
						]
					),
				],
			)
		)

	def _register_callbacks(self):
		if self._callbacks_registered:
			print("Callbacks already registered!")
			return

		# sync date preset with date inputs
		@self.register_callback(
			output=(dash.Output("filter-date-from", "value"), dash.Output("filter-date-to", "value")),
			inputs=(dash.Input("filter-date-preset", "value")),
		)
		def sync_date_preset(preset):
			return days[preset] if preset in days else (days['1'][0], days['3'][1])

		# FIXME: register cashflow section callbacks
		# cashflow_section_callbacks(self)

		# register performance section callbacks
		performance_section_callbacks(self)

		# FIXME: update orders insights section
		# @self.register_callback(
		# 	background=True,
		# 	output=(dash.Output("order-insights-section", "children")),
		# 	inputs=(
		# 			dash.Input(component_id="filter-date-from", component_property="value"),
		# 			dash.Input(component_id="filter-date-to", component_property="value"),
		# 	),
		# )
		async def update_orders_insights_section(date_from, date_to):
			results = await self.query_manager.execute_queries(
				query_names=[
					"order_sales_stats",
					"vip_order_sales_stats",
					"order_refunds_stats",
					"cups_stats",
					"organizer_revenue",
					"transaction_volume",
					"customer_base",
					"chip_refunds",
				],
				parameters={
					"date_from": dateutil.parser.parse(date_from),
					"date_to": dateutil.parser.parse(date_to)
				}
			)
			# sales_overview = results["total_sales_overview"].iloc[0]
			order_sales_stats = results["order_sales_stats"].iloc[0]
			vip_order_sales_stats = results["vip_order_sales_stats"].iloc[0]
			order_refunds_stats = results["order_refunds_stats"].iloc[0]
			cups_stats_sold = results["cups_stats"].iloc[0]
			cups_stats_returned = results["cups_stats"].iloc[1]

			org_revenue = results['organizer_revenue']

			chip_refunds = results['chip_refunds'].iloc[0]

			trans_volume = results['transaction_volume'].iloc[0]
			cust_base = results['customer_base'].iloc[0]
			cust_base_types = {
				"Regular chips": cust_base['regular_chips'],
				"Online top-up": cust_base['online_chips'],
				"VIP chips": cust_base['vip_chips'],
				"Staff chips": cust_base['staff_chips'],
				"Guest chips": cust_base['guest_chips'],
			}
			top_cust_base = sorted(cust_base_types.items(), key=lambda x: x[1], reverse=True)[:1]
			top_cust_base_stats = pd.DataFrame(
				[{
					"name": name,
					"count": count,
					"percentage": count / cust_base['total_chips'] * 100 if count > 0 else 0
				} for name, count in top_cust_base]
			)

			return [
				# Total Sales Card
				dmc.GridCol(
					span=3,
					children=[
						dmc.Card(
							className="h-full",
							withBorder=True,
							children=[
								dmc.Stack(
									gap="xs",
									children=[
										dmc.Text("Total Sales", size="sm", fw=500),
										dmc.Text(
											format_price(
												order_sales_stats['total_amount'] +
												vip_order_sales_stats['total_amount'] +
												order_refunds_stats['total_amount']
											),
											size="xl",
											fw=700
										),
										dmc.Text(
											format_price(
												order_sales_stats['total_amount_without_vat'] +
												vip_order_sales_stats['total_amount_without_vat'] +
												order_refunds_stats['total_amount_without_vat']
											) + " without VAT",
											size="sm",
											c="dimmed"
										),
										dmc.Divider(className="my-2"),
										dmc.Stack(
											gap="xs",
											children=[
												dmc.Group(
													children=[
														html.Div(
															className="flex items-center gap-1",
															children=[
																dmc.Text(f"Regular Sales", size="sm"),
																dmc.Badge(format_number_short(order_sales_stats['total_count']), size="xs", variant="light", color="black"),
															]
														),
														dmc.Text(
															format_price(order_sales_stats['total_amount']),
															className="ml-auto",
															size="sm",
															fw=500
														)
													]
												),
												dmc.Group(
													justify="space-between",
													children=[
														html.Div(
															className="flex items-center gap-1",
															children=[
																dmc.Text(f"Cups returned", size="sm"),
																dmc.Badge(format_number_short(cups_stats_returned['total_count']), size="xs", variant="light", color="black"),
															]
														),
														dmc.Text(
															format_price(
																cups_stats_returned['total_amount']
															),
															size="sm",
															fw=500
														)
													]
												),
												dmc.Group(
													justify="space-between",
													children=[
														html.Div(
															className="flex items-center gap-1",
															children=[
																dmc.Text(f"Order refunds", size="sm"),
																dmc.Badge(format_number_short(order_refunds_stats['total_count'] - cups_stats_returned['total_count']), size="xs", variant="light", color="black"),
															]
														),
														dmc.Text(
															format_price(
																order_refunds_stats['total_amount']
																- cups_stats_returned['total_amount']
															),
															size="sm",
															fw=500
														)
													]
												),
												dmc.Group(
													justify="space-between",
													children=[
														html.Div(
															className="flex items-center gap-1",
															children=[
																dmc.Text(f"VIP Orders", size="sm"),
																dmc.Badge(format_number_short(vip_order_sales_stats['total_count']), size="xs", variant="light", color="black"),
															]
														),
														dmc.Text(
															format_price(vip_order_sales_stats['total_amount']),
															size="sm",
															fw=500
														)
													]
												),
											]
										)
									]
								)
							]
						)
					]
				),

				# Organizer Revenue Card
				dmc.GridCol(
					span=3,
					children=[
						dmc.Card(
							className="h-full",
							withBorder=True,
							children=[
								dmc.Stack(
									gap="xs",
									className="grow",
									children=[
										dmc.Text("Organizer's Revenue", size="sm", fw=500),
										dmc.Text(
											format_price(
												org_revenue['commission_revenue'].sum() +
												chip_refunds['unclaimed_balance']
											),
											size="xl",
											fw=700
										),
										dmc.Text(
											"from sales and Non-refunded balance",
											size="sm",
											c="dimmed"
										),
										dmc.Divider(className="my-2"),
										dmc.SimpleGrid(
											cols=1,
											spacing="xs",
											className="grow",
											children=[
												dmc.Group(
													justify="space-between",
													children=[
														dmc.Text("Sale commission", size="sm"),
														dmc.Text(
															format_price(org_revenue['commission_revenue'].sum()),
															size="sm",
															fw=500
														)
													]
												),
												dmc.Group(
													justify="space-between",
													children=[
														dmc.Text("Non-refunded Balance", size="sm"),
														dmc.Text(
															format_price(chip_refunds['unclaimed_balance']),
															size="sm",
															fw=500
														)
													]
												),
												dmc.Button(
													className="mt-auto",
													variant="light",
													color="gray",
													disabled=True,
													children="View cash flows",
												)
											]
										)
									]
								)
							]
						)
					]
				),

				# Transaction Volume Card
				dmc.GridCol(
					span=3,
					children=[
						dmc.Card(
							className="h-full",
							withBorder=True,
							children=[
								dmc.Stack(
									gap="xs",
									children=[
										dmc.Text("Transaction Volume", size="sm", fw=500),
										dmc.Text(
											f"{format_number(trans_volume['total_transactions'])} transactions",
											size="xl",
											fw=700
										),
										dmc.Group(
											justify="space-between",
											children=[
												dmc.Text("Average per Hour", size="sm", c="dimmed"),
												dmc.Text(format_number(trans_volume['avg_per_hour']), size="sm", c="dimmed"),
											]
										),
										dmc.Divider(className="my-2"),
										dmc.Stack(
											gap="xs",
											children=[
												dmc.Group(
													justify="space-between",
													children=[
														dmc.Text("Orders range", size="sm"),
														dmc.Text(
															children=[
																f"{format_price(order_sales_stats['min_amount'])} – {format_price(order_sales_stats['max_amount'])}",
															],
															size="sm", fw=500
														)
													]
												),
												dmc.Group(
													justify="space-between",
													children=[
														dmc.Text("Top-up Transactions", size="sm"),
														dmc.Text(format_number(trans_volume['topup_transactions']), size="sm", fw=500)
													]
												),
												dmc.Group(
													justify="space-between",
													children=[
														dmc.Text("Sales Orders", size="sm"),
														dmc.Text(format_number(trans_volume['sale_orders']), size="sm", fw=500)
													]
												),
												dmc.Group(
													justify="space-between",
													children=[
														dmc.Text("Refund Orders", size="sm"),
														dmc.Text(format_number(trans_volume['refund_orders']), size="sm", fw=500)
													]
												),
											]
										)
									]
								)
							]
						)
					]
				),

				# Customer Base Card
				dmc.GridCol(
					span=3,
					children=[
						dmc.Card(
							className="h-full",
							withBorder=True,
							children=[
								dmc.Stack(
									gap="xs",
									children=[
										dmc.Text("Active Customers", size="sm", fw=500),
										dmc.Text(
											f"{format_number(cust_base['total_chips'])} unique chips",
											size="xl",
											fw=700
										),
										dmc.Text(
											"total in the system",
											size="sm",
											c="dimmed"
										),
										dmc.Divider(className="my-2"),
										*[dmc.Stack(
											gap=2,
											children=[
												dmc.Group(
													justify="space-between",
													children=[
														dmc.Text(row['name'], size="sm"),
														dmc.Text(
															f"{format_number(row['count'])} ({row['percentage']:.1f}%)",
															size="sm",
															fw=500
														)
													]
												),
												dmc.Progress(
													value=row['percentage'],
													color="red",
													size="sm"
												)
											]
										)
											for _, row in top_cust_base_stats.iterrows()
										],
										dmc.Divider(className="my-2"),
										dmc.Group(
											justify="space-between",
											children=[
												dmc.Text("Non-refunded Chips", size="sm"),
												dmc.Text(
													format_number(chip_refunds['unclaimed_chips']),
													size="sm",
													fw=500
												)
											]
										),
										dmc.Group(
											justify="space-between",
											children=[
												dmc.Text("Blocked chips", size="sm"),
												dmc.Text(
													format_number(chip_refunds['blocked_chips']),
													size="sm",
													fw=500
												)
											]
										),
									]
								)
							]
						)
					]
				),
			]

		self._callbacks_registered = True

	@property
	def app(self):
		return self.__app


# Run the app
if __name__ == '__main__':
	Application = MainApplication()
	app = Application.app
	app.run_server(debug=True, port=4001)
# app.run_server(debug=False, host='192.168.0.167', port=4000)


#  old
# # -- TODO: Customer insights section
# html.Section(
# 	className="flex flex-col gap-3 bg-white rounded-lg border border-zinc-200",
# 	children=[
# 		html.Div(
# 			className="p-4",
# 			children=[
# 				html.Div(
# 					className="flex items-center gap-4",
# 					children=[
# 						dmc.ThemeIcon(
# 							size="xl",
# 							radius="xl",
# 							c="indigo",
# 							variant="light",
# 							children=DashIconify(icon="carbon:customer", width=25)
# 						),
# 						html.Div(
# 							children=[
# 								dmc.Title(
# 									size="1.25rem",
# 									children='Customer insights (Online vs. Onsite)'
# 								),
# 								dmc.Text(
# 									"TODO: detailed description here",
# 									c="dimmed",
# 								),
# 							]
# 						)
# 					],
# 				),
# 			]
# 		),
# 		# Overview
# 		dmc.Grid(
# 			gutter="md",
# 			p="sm",
# 			grow=False,
# 			children=[
# 				dmc.GridCol(
# 					span=12,
# 					children=[
# 						dcc.Loading(
# 							type="dot",
# 							target_components={ "customer-insights-left-results": "children" },
# 							children=[
# 								# Content tabs
# 								dmc.Tabs(
# 									id="customer-insights-left-results",
# 									value="activity",
# 									children=[],
# 								),
# 							],
# 						),
# 						# dmc.Card(
# 						# 	withBorder=True,
# 						# 	children=[
# 						# 		html.Div(
# 						# 			className="grid grid-cols-1 gap-3",
# 						# 			children=[
# 						# 				dmc.Select(
# 						# 					id="customer-insights-left-grouping",
# 						# 					allowDeselect=False,
# 						# 					value="chip_group:Online",
# 						# 					data=customer_insights_grouping_options,
# 						# 				),
# 						# 				# dcc.Loading(
# 						# 				# 	type="dot",
# 						# 				# 	target_components={ "customer-insights-left-results": "children" },
# 						# 				# 	children=[
# 						# 				# 		html.Div(
# 						# 				# 			id="customer-insights-left-results",
# 						# 				# 			children=[]
# 						# 				# 		)
# 						# 				# 	],
# 						# 				# ),
# 						# 			]
# 						# 		)
# 						# 	]
# 						# )
# 					]
# 				),
# 				# FIXME
# 				# dmc.GridCol(
# 				# 	span=6,
# 				# 	children=[
# 				# 		dmc.Card(
# 				# 			withBorder=True,
# 				# 			children=[
# 				# 				html.Div(
# 				# 					className="grid grid-cols-1 gap-3",
# 				# 					children=[
# 				# 						dmc.Select(
# 				# 							id="customer-insights-right-grouping",
# 				# 							allowDeselect=False,
# 				# 							value="chip_group:Onsite",
# 				# 							data=customer_insights_grouping_options,
# 				# 						),
# 				# 						dcc.Loading(
# 				# 							type="dot",
# 				# 							target_components={ "customer-insights-right-results": "children" },
# 				# 							children=[
# 				# 								html.Div(
# 				# 									id="customer-insights-right-results",
# 				# 									children=[]
# 				# 								)
# 				# 							],
# 				# 						),
# 				# 					]
# 				# 				)
# 				# 			]
# 				# 		)
# 				# 	]
# 				# )
# 			]
# 		),
# 	],
# ),
# # -- Main overview section
# html.Section(
# 	className="flex flex-col gap-3 bg-white rounded-lg border border-zinc-200",
# 	children=[
# 		html.Div(
# 			className="p-4",
# 			children=[
# 				html.Div(
# 					className="flex items-center gap-4",
# 					children=[
# 						dmc.ThemeIcon(
# 							size="xl",
# 							radius="xl",
# 							c="indigo",
# 							variant="light",
# 							children=DashIconify(icon="mdi:performance", width=25)
# 						),
# 						html.Div(
# 							children=[
# 								dmc.Title(
# 									size="1.25rem",
# 									children='Main overview'
# 								),
# 								dmc.Text(
# 									"TODO: detailed description here",
# 									c="dimmed",
# 								),
# 							]
# 						)
# 					],
# 				),
# 			]
# 		),
# 		# Overview
# 		dcc.Loading(
# 			type="dot",
# 			target_components={ "order-insights-section": "children" },
# 			children=[
# 				dmc.Grid(
# 					id="order-insights-section",
# 					gutter="md",
# 					p="sm",
# 					grow=False,
# 					children=[]
# 				)
# 			],
# 		),
# 		# Content tabs
# 		dmc.Tabs(
# 			id="order-insights-section-tabs",
# 			value="time-series",
# 			children=[
# 				html.Div(
# 					className="px-3",
# 					children=[
# 						dmc.TabsList(
# 							children=[
# 								dmc.TabsTab(
# 									"Time Series",
# 									leftSection=DashIconify(icon="tabler:chart-line"),
# 									value="time-series",
# 								),
# 								dmc.TabsTab(
# 									"Cash Flows",
# 									leftSection=DashIconify(icon="tabler:cash"),
# 									value="cash-flow",
# 								),
# 							]
# 						),
# 					]
# 				),
# 				# time series tab
# 				dmc.TabsPanel(
# 					value="time-series",
# 					children=[
# 						dmc.Grid(
# 							gutter="md",
# 							p="sm",
# 							grow=False,
# 							children=[
# 								# TODO: Main Chart
# 								dmc.GridCol(
# 									span=12,
# 									children=[
# 										# Time Series Chart Panel
# 										dmc.Card(
# 											withBorder=True,
# 											children=[
# 												# Header with controls
# 												dmc.Group(
# 													justify="space-between",
# 													className="mb-4",
# 													children=[
# 														dmc.Text("Sales Over Time", size="lg", fw=500),
# 														dmc.Group(
# 															children=[
# 																dmc.Switch(
# 																	id="include-vip-toggle",
# 																	label="Include VIP",
# 																	checked=True
# 																)
# 															]
# 														)
# 													]
# 												),
# 												# Line Chart
# 												dcc.Loading(
# 													type="dot",
# 													target_components={ "time-series-line-chart": "children" },
# 													children=[
# 														html.Div(id="time-series-line-chart"),
# 													],
# 												),
# 											]
# 										),
# 									]
# 								),
# 							]
# 						),
# 					]
# 				),
# 				# cash flow tab
# 				dmc.TabsPanel(
# 					value="cash-flow",
# 					children=[
# 						dcc.Loading(
# 							type="dot",
# 							target_components={ "cash-flow-section": "children" },
# 							children=[
# 								dmc.Grid(
# 									id="cash-flow-section",
# 									gutter="md",
# 									p="sm",
# 									grow=False,
# 									children=[]
# 								),
# 							],
# 						),
# 					]
# 				),
# 			],
# 		)
# 	],
# ),
# # TODO: Footer
# html.Footer(
# 	className="fixed bottom-0 left-0 right-0 p-4 bg-white border-t border-zinc-200",
# 	children=[
# 		html.Div(
# 			className="container mx-auto",
# 			children=[
# 				html.Div(
# 					className="flex items-center gap-2",
# 					children=[
# 						dmc.DateTimePicker(
# 							id="filter-date-from",
# 							label="Filter from",
# 							value="2024-07-04T00:00:00",
# 							w=250,
# 						),
# 						dmc.DateTimePicker(
# 							id="filter-date-to",
# 							label="Filter to",
# 							value="2024-07-07T23:59:59",
# 							w=250,
# 						),
# 						dmc.Select(
# 							label="Select date",
# 							id="filter-date-preset",
# 							allowDeselect=False,
# 							value="all",
# 							data=[
# 								{ "value": "1", "label": "Day 1" },
# 								{ "value": "2", "label": "Day 2" },
# 								{ "value": "3", "label": "Day 3" },
# 								{ "value": "all", "label": "Whole festival" },
# 							],
# 							w=200,
# 						),
# 					]
# 				)
# 			]
# 		),
# 	],
# )
