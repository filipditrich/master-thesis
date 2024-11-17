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

from chart_utils import SankeyDiagram
from dash_utils import background_callback_manager, create_cache_key, external_script, index_string
from db_queries import query_manager
from db_utils import format_date, format_number, format_number_short, format_percent, format_price

# set the React version
dash._dash_renderer._set_react_version("18.2.0")

# (day starts at 06:00am, day ends 05:59am +1 next day)
days = {
	'1': ('2024-07-04 06:00:00', '2024-07-05 05:59:59'),
	'2': ('2024-07-05 06:00:00', '2024-07-06 05:59:59'),
	'3': ('2024-07-06 06:00:00', '2024-07-07 05:59:59'),
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

		# Register callbacks
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

		# customer_insights_grouping_options = [
		# 	# all
		# 	# {
		# 	# 	"group": "All",
		# 	# 	"items": [
		# 	# 		{ "value": "all:all", "label": "All customers" },
		# 	# 	]
		# 	# },
		# 	# per type
		# 	{
		# 		"group": "Chip type",
		# 		"items": [
		# 			{ "value": "chip_type:Pass", "label": "Tickets customers" },
		# 			{ "value": "chip_type:POS", "label": "POS customers" },
		# 			{ "value": "chip_type:POS VIP", "label": "POS VIP customers" },
		# 			{ "value": "chip_type:Guest", "label": "Guset customers" },
		# 			{ "value": "chip_type:Staff", "label": "Staff customers" },
		# 		]
		# 	},
		# 	# per group
		# 	{
		# 		"group": "Chip group",
		# 		"items": [
		# 			{ "value": "chip_group:Onsite", "label": "Onsite customers" },
		# 			{ "value": "chip_group:Online", "label": "Online customers" },
		# 		]
		# 	},
		# 	# per bank
		# 	{
		# 		"group": "Bank",
		# 		"items": [
		# 			{ "value": "bank:5500", "label": "Raiffeisenbank" },
		# 			{ "value": "bank:3030", "label": "Air Bank" },
		# 			{ "value": "bank:2010", "label": "Fio banka" },
		# 			{ "value": "bank:6210", "label": "mBank" },
		# 			{ "value": "bank:2700", "label": "UniCredit Bank" },
		# 			{ "value": "bank:0800", "label": "Česká spořitelna" },
		# 			{ "value": "bank:0300", "label": "ČSOB" },
		# 			{ "value": "bank:0100", "label": "Komerční banka" },
		# 			{ "value": "bank:2250", "label": "Banka CREDITS" },
		# 			{ "value": "bank:0600", "label": "MONETA Money Bank" },
		# 			{ "value": "bank:6363", "label": "Partners Banka" },
		# 			# TODO: more options
		# 		]
		# 	}
		# 	# TODO
		# ]

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
							# FIXME
							fast_preview_playground(),
							# Main content
							html.Main(
								className="grid grid-cols-1 gap-4",
								children=[
									# -- TODO: Customer insights section
									html.Section(
										className="flex flex-col gap-3 bg-white rounded-lg border border-zinc-200",
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
																c="indigo",
																variant="light",
																children=DashIconify(icon="carbon:customer", width=25)
															),
															html.Div(
																children=[
																	dmc.Title(
																		size="1.25rem",
																		children='Customer insights (Online vs. Onsite)'
																	),
																	dmc.Text(
																		"TODO: detailed description here",
																		c="dimmed",
																	),
																]
															)
														],
													),
												]
											),
											# Overview
											dmc.Grid(
												gutter="md",
												p="sm",
												grow=False,
												children=[
													dmc.GridCol(
														span=12,
														children=[
															dcc.Loading(
																type="dot",
																target_components={ "customer-insights-left-results": "children" },
																children=[
																	# Content tabs
																	dmc.Tabs(
																		id="customer-insights-left-results",
																		value="activity",
																		children=[],
																	),
																],
															),
															# dmc.Card(
															# 	withBorder=True,
															# 	children=[
															# 		html.Div(
															# 			className="grid grid-cols-1 gap-3",
															# 			children=[
															# 				dmc.Select(
															# 					id="customer-insights-left-grouping",
															# 					allowDeselect=False,
															# 					value="chip_group:Online",
															# 					data=customer_insights_grouping_options,
															# 				),
															# 				# dcc.Loading(
															# 				# 	type="dot",
															# 				# 	target_components={ "customer-insights-left-results": "children" },
															# 				# 	children=[
															# 				# 		html.Div(
															# 				# 			id="customer-insights-left-results",
															# 				# 			children=[]
															# 				# 		)
															# 				# 	],
															# 				# ),
															# 			]
															# 		)
															# 	]
															# )
														]
													),
													# FIXME
													# dmc.GridCol(
													# 	span=6,
													# 	children=[
													# 		dmc.Card(
													# 			withBorder=True,
													# 			children=[
													# 				html.Div(
													# 					className="grid grid-cols-1 gap-3",
													# 					children=[
													# 						dmc.Select(
													# 							id="customer-insights-right-grouping",
													# 							allowDeselect=False,
													# 							value="chip_group:Onsite",
													# 							data=customer_insights_grouping_options,
													# 						),
													# 						dcc.Loading(
													# 							type="dot",
													# 							target_components={ "customer-insights-right-results": "children" },
													# 							children=[
													# 								html.Div(
													# 									id="customer-insights-right-results",
													# 									children=[]
													# 								)
													# 							],
													# 						),
													# 					]
													# 				)
													# 			]
													# 		)
													# 	]
													# )
												]
											),
										],
									),
									# -- Main overview section
									html.Section(
										className="flex flex-col gap-3 bg-white rounded-lg border border-zinc-200",
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
																c="indigo",
																variant="light",
																children=DashIconify(icon="mdi:performance", width=25)
															),
															html.Div(
																children=[
																	dmc.Title(
																		size="1.25rem",
																		children='Main overview'
																	),
																	dmc.Text(
																		"TODO: detailed description here",
																		c="dimmed",
																	),
																]
															)
														],
													),
												]
											),
											# Overview
											dcc.Loading(
												type="dot",
												target_components={ "order-insights-section": "children" },
												children=[
													dmc.Grid(
														id="order-insights-section",
														gutter="md",
														p="sm",
														grow=False,
														children=[]
													)
												],
											),
											# Content tabs
											dmc.Tabs(
												id="order-insights-section-tabs",
												value="time-series",
												children=[
													html.Div(
														className="px-3",
														children=[
															dmc.TabsList(
																children=[
																	dmc.TabsTab(
																		"Time Series",
																		leftSection=DashIconify(icon="tabler:chart-line"),
																		value="time-series",
																	),
																	dmc.TabsTab(
																		"Cash Flows",
																		leftSection=DashIconify(icon="tabler:cash"),
																		value="cash-flow",
																	),
																]
															),
														]
													),
													# time series tab
													dmc.TabsPanel(
														value="time-series",
														children=[
															dmc.Grid(
																gutter="md",
																p="sm",
																grow=False,
																children=[
																	# TODO: Main Chart
																	dmc.GridCol(
																		span=12,
																		children=[
																			# Time Series Chart Panel
																			dmc.Card(
																				withBorder=True,
																				children=[
																					# Header with controls
																					dmc.Group(
																						justify="space-between",
																						className="mb-4",
																						children=[
																							dmc.Text("Sales Over Time", size="lg", fw=500),
																							dmc.Group(
																								children=[
																									dmc.Switch(
																										id="include-vip-toggle",
																										label="Include VIP",
																										checked=True
																									)
																								]
																							)
																						]
																					),
																					# Line Chart
																					dcc.Loading(
																						type="dot",
																						target_components={ "time-series-line-chart": "children" },
																						children=[
																							html.Div(id="time-series-line-chart"),
																						],
																					),
																				]
																			),
																		]
																	),
																]
															),
														]
													),
													# cash flow tab
													dmc.TabsPanel(
														value="cash-flow",
														children=[
															dcc.Loading(
																type="dot",
																target_components={ "cash-flow-section": "children" },
																children=[
																	dmc.Grid(
																		id="cash-flow-section",
																		gutter="md",
																		p="sm",
																		grow=False,
																		children=[]
																	),
																],
															),
														]
													),
												],
											)
										],
									),
								]
							),
						]
					),

					# TODO: Footer
					html.Footer(
						className="fixed bottom-0 left-0 right-0 p-4 bg-white border-t border-zinc-200",
						children=[
							html.Div(
								className="container mx-auto",
								children=[
									html.Div(
										className="flex items-center gap-2",
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
													{ "value": "all", "label": "Whole festival" },
												],
												w=200,
											),
										]
									)
								]
							),
						],
					)
				],
			)
		)

	async def update_customer_insights_results(self, date_from, date_to, grouping_key, main_value, comp_value):
		print(f"Grouping key: {grouping_key}, value: {main_value} (vs. {comp_value})")

		# all_results = await self.query_manager.execute_queries(
		# 	query_names=[
		# 		"customer_order_stats_grouped",
		# 		"customer_topup_stats_grouped",
		# 		"customer_activity_stats_grouped",
		# 		"customer_refund_stats_grouped"
		# 	],
		# 	parameters={
		# 		"date_from": dateutil.parser.parse(date_from),
		# 		"date_to": dateutil.parser.parse(date_to),
		# 		"grouping_key": 'all'
		# 	}
		# )
		# all_data = pd.concat(
		# 	[
		# 		all_results['customer_order_stats_grouped'].iloc[0],
		# 		all_results['customer_topup_stats_grouped'].iloc[0],
		# 		all_results['customer_activity_stats_grouped'].iloc[0],
		# 		all_results['customer_refund_stats_grouped'].iloc[0],
		# 	]
		# )
		results = await self.query_manager.execute_queries(
			query_names=[
				"customer_order_stats_grouped",
				"customer_topup_stats_grouped",
				"customer_activity_stats_grouped",
				"customer_refund_stats_grouped"
			],
			parameters={
				"date_from": dateutil.parser.parse(date_from),
				"date_to": dateutil.parser.parse(date_to),
				"grouping_key": grouping_key
			}
		)
		# TODO
		customers_order_stats_grouped = results['customer_order_stats_grouped']
		customers_topup_stats_grouped = results['customer_topup_stats_grouped']
		customers_activity_stats_grouped = results['customer_activity_stats_grouped']
		customers_refund_stats_grouped = results['customer_refund_stats_grouped']
		# get first row af all stats data and merge their columns to one
		main_data = pd.concat(
			[
				customers_order_stats_grouped[customers_order_stats_grouped['grouping_key'] == main_value].iloc[0],
				customers_topup_stats_grouped[customers_topup_stats_grouped['grouping_key'] == main_value].iloc[0],
				customers_activity_stats_grouped[customers_activity_stats_grouped['grouping_key'] == main_value].iloc[0],
				customers_refund_stats_grouped[customers_refund_stats_grouped['grouping_key'] == main_value].iloc[0],
			]
		)

		# right_data = pd.concat(
		# 	[
		# 		customers_order_stats_grouped[customers_order_stats_grouped['grouping_key'] == comp_value].iloc[0],
		# 		customers_topup_stats_grouped[customers_topup_stats_grouped['grouping_key'] == comp_value].iloc[0],
		# 		customers_activity_stats_grouped[customers_activity_stats_grouped['grouping_key'] == comp_value].iloc[0],
		# 		customers_refund_stats_grouped[customers_refund_stats_grouped['grouping_key'] == comp_value].iloc[0],
		# 	]
		# ) if comp_value else _all_data

		# daily_customers = pd.DataFrame(json.loads(main_data['activity_daily_customers']))

		def stat_item(name, value, change=None):
			return dmc.Group(
				justify="space-between",
				children=[
					dmc.Text(name, size="sm"),
					dmc.Text(value, size="sm", fw=600),
				]
			)

		# def get_value_of(key, inverse=False):
		# 	try:
		# 		ref_value = left_data[key]
		# 		if inverse:
		# 			all_value = all_data[key]
		# 			return all_value - ref_value
		#
		# 		return ref_value
		#
		# 	except Exception as e:
		# 		return 0
		#
		# def get_ratio_of(key, inverse=False):
		# 	try:
		# 		ref_value = left_data[key]
		# 		value = (ref_value / all_data[key]) * 100
		# 		if inverse:
		# 			return 100 - value
		# 		return value
		# 	except Exception as e:
		# 		return 0
		#
		# def get_percentage_change_of(key):
		# 	try:
		# 		ref_value = get_value_of(key)
		# 		rest_value = get_value_of(key, True)
		# 		return ((ref_value - rest_value) / rest_value) * 100
		# 	except Exception as e:
		# 		return 0

		# capitalize
		# left_label = main_value.capitalize()
		# right_label = "Rest"  # fixme
		# left_color = "blue"
		# right_color = "pink"

		return [
			html.Div(
				children=[
					dmc.TabsList(
						children=[
							dmc.TabsTab("Activity", leftSection=DashIconify(icon="mdi:chart-line"), value="activity"),
							dmc.TabsTab("Orders", leftSection=DashIconify(icon="mdi:cart"), value="orders"),
						]
					),
					# activity tab
					dmc.TabsPanel(
						value="activity",
						children=[
							dmc.Grid(
								py="sm",
								children=[
									# customers card
									dmc.GridCol(
										span=3,
										children=[
											dmc.Card(
												className="h-full",
												withBorder=True,
												children=[
													dmc.Stack(
														className="grow",
														gap="xs",
														children=[
															dmc.Group(
																justify="space-between",
																children=[
																	dmc.Text("Total Active Customers", size="sm", fw=500),
																	DashIconify(icon="mdi:account-group", width=21)
																]
															),
															dmc.Text(
																children=[
																	f"{format_number(main_data['total_customers'])} unique customers"
																], size="xl", fw=700
															),
															dmc.Divider(className="mt-auto"),
														]
													)
												]
											),
										]
									),
									# top-ups card
									dmc.GridCol(
										span=4,
										children=[
											dmc.Card(
												className="h-full",
												withBorder=True,
												children=[
													dmc.Stack(
														gap="xs",
														children=[
															dmc.Group(
																justify="space-between",
																children=[
																	dmc.Text("Top-ups volume", size="sm", fw=500),
																	DashIconify(icon="mdi:credit-card", width=21)
																]
															),
															dmc.Text(
																children=[
																	format_price(main_data['topup_total_amount'])
																], size="1.5rem", fw=700
															),
															dmc.Text(
																children=[
																	f"{format_number(main_data['topup_total_count'])} top-ups (max. {format_number(main_data['topup_max_count'])} per customer)"
																], size="sm", c="dimmed"
															),
															dmc.Divider(className="mt-auto"),
															dmc.Stack(
																gap="xs",
																children=[
																	# stat_item("Total top-ups", format_number(main_data['topup_total_count'])),
																	# stat_item("Average top-up amount", format_price(main_data['topup_avg_amount'])),
																	stat_item("Average top-up count", format_number(main_data['topup_avg_count'])),
																]
															),
															dmc.Grid(
																children=[
																	dmc.GridCol(
																		span=6,
																		children=dmc.Card(
																			withBorder=True,
																			p="xs",
																			className="bg-gray-50",
																			children=[
																				dmc.Group(
																					gap=4,
																					children=[
																						DashIconify(icon="mdi:credit-card", width=14, color="gray"),
																						dmc.Text("Average top-up", size="xs", c="dimmed", fw=600),
																					]
																				),
																				dmc.Text(children=format_price(main_data['topup_avg_amount']), size="lg", fw=700),
																			]
																		)
																	),
																	dmc.GridCol(
																		span=6,
																		children=dmc.Card(
																			withBorder=True,
																			p="xs",
																			className="bg-gray-50",
																			children=[
																				dmc.Group(
																					gap=4,
																					children=[
																						DashIconify(icon="mdi:credit-card", width=14, color="gray"),
																						dmc.Text("Average top-up", size="xs", c="dimmed", fw=600),
																					]
																				),
																				dmc.Text(children=format_price(main_data['topup_avg_amount']), size="lg", fw=700),
																			]
																		)
																	)
																]
															),
														]
													)
												]
											),
										]
									),
								]
							),
						]
					),
					# orders tab
					dmc.TabsPanel(
						value="orders",
						children=[
							dmc.Grid(
								py="sm",
								children=[
									dmc.GridCol(
										span=3,
										children=["TODO"]
									)
								]
							)
						]
					)
				]
			),
		]

		# dmc.Stack(
		# 	gap=4,
		# 	children=[
		# 		dmc.Group(
		# 			justify="space-between",
		# 			children=[
		# 				dmc.Text(f"{left_label} ({format_percent(get_ratio_of('total_customers'))})", size="xs", c="dimmed"),
		# 				dmc.Text(right_label, size="xs", c="dimmed"),
		# 			]
		# 		),
		# 		dmc.ProgressRoot(
		# 			[
		# 				dmc.ProgressSection(value=get_ratio_of('total_customers'), color=left_color),
		# 				dmc.ProgressSection(value=get_ratio_of('total_customers', True), color=right_color),
		# 			],
		# 			size="sm",
		# 		),
		# 		dmc.Group(
		# 			justify="space-between",
		# 			children=[
		# 				dmc.Text(format_number(get_value_of('total_customers')), size="xs", fw=500),
		# 				dmc.Text(format_number(get_value_of('total_customers', True)), size="xs", fw=500)
		# 			]
		# 		),
		# 	]
		# ),

		return [
			html.Div(
				className="flex flex-col gap-3 p-2",
				children=[

					# Overview
					html.Header(
						className="flex items-center gap-2 justify-between",
						children=[
							dmc.Text("Customers Overview", size="lg", fw=500),
							DashIconify(icon="mdi:account-group", width=21)
						]
					),
					dmc.Stack(
						gap="xs",
						children=[
							stat_item("Total customers", format_number(main_data['total_customers'])),
						]
					),
					# Orders
					html.Header(
						className="flex items-center gap-2 justify-between",
						children=[
							dmc.Text("Orders Overview", size="lg", fw=500),
							DashIconify(icon="mdi:cart", width=21)
						]
					),
					dmc.Stack(
						gap="xs",
						children=[
							stat_item("Total orders", format_number(main_data['order_total_count'])),
							stat_item("Total orders volume", format_price(main_data['order_total_amount'])),
							stat_item(
								"Top category",
								f"{main_data['order_top_category']} ({format_number(main_data['order_top_category_ratio'])} %)"
							),
							stat_item(
								"Top product",
								f"{main_data['order_top_product']} ({format_number(main_data['order_top_product_ratio'])} %)"
							),
							stat_item(
								"Top place",
								f"{main_data['order_top_place']} ({format_number(main_data['order_top_place_ratio'])} %)"
							),
							stat_item("Average order value", format_price(main_data['order_avg_amount'])),
							stat_item("Average total spent", format_price(main_data['order_avg_spending'])),
							stat_item("Average time between orders", f"{format_number(main_data['order_avg_hours_between'])} hours"),
						]
					),
					# Top ups
					html.Header(
						className="flex items-center gap-2 justify-between",
						children=[
							dmc.Text("Top-ups Overview", size="lg", fw=500),
							DashIconify(icon="mdi:credit-card", width=21)
						]
					),
					dmc.Stack(
						gap="xs",
						children=[
							stat_item("Total top-ups", format_number(main_data['topup_total_count'])),
							stat_item("Total top-ups volume", format_price(main_data['topup_total_amount'])),
							stat_item("Max top-up amount", format_price(main_data['topup_max_amount'])),
							stat_item("Average top-up amount", format_price(main_data['topup_avg_amount'])),
							stat_item("Max top-up count", format_number(main_data['topup_max_count'])),
							stat_item("Average top-up count", format_number(main_data['topup_avg_count'])),
							stat_item("Average time between top-ups", f"{format_number(main_data['topup_avg_hours_between'])} hours"),
							stat_item("Top top-up place", f"{main_data['topup_top_place']} ({format_number(main_data['topup_top_place_ratio'])} %)"),
						]
					),
					# Activity ups
					html.Header(
						className="flex items-center gap-2 justify-between",
						children=[
							dmc.Text("Activity overview", size="lg", fw=500),
							DashIconify(icon="mdi:chart-line", width=21)
						]
					),
					dmc.Stack(
						gap="xs",
						children=[
							stat_item("Average time spent", f"{format_number(main_data['activity_avg_hours'])} hours"),
							stat_item("Max time spent", f"{format_number(main_data['activity_max_hours'])} hours"),
							stat_item("Average sessions", format_number(main_data['activity_avg_sessions'])),
							stat_item("Average session length", f"{format_number(main_data['activity_avg_session_length'])} hours"),
							stat_item("Customers who rated", f"{format_number(main_data['active_customers_with_ratings'])} ({format_number(main_data['active_customers_with_ratings_ratio'])} %)"),
							stat_item("Average rating", f"{format_number(main_data['activity_avg_rating'])}"),
							stat_item("Blocked customers", f"{format_number(main_data['blocked_customers'])} ({format_number(main_data['blocked_customers_ratio'])} %)"),
							# activity avg daily customers, max, min
							stat_item("Average daily customers", format_number(main_data['activity_avg_daily_customers'])),
							stat_item("Max daily customers", format_number(main_data['activity_max_daily_customers'])),
							stat_item("Min daily customers", format_number(main_data['activity_min_daily_customers'])),
							*[
								stat_item(
									f"Daily: {format_date(row['date'])}",
									format_number(row['active_customers']),
								)
								for _, row in daily_customers.iterrows()
							]
						]
					),
				]
			)
		]

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

		# FIXME: update customers insights section (left)
		@self.register_callback(
			background=True,
			output=(dash.Output("customer-insights-left-results", "children")),
			inputs=(
					dash.Input("filter-date-from", "value"),
					dash.Input("filter-date-to", "value"),
					# dash.Input("customer-insights-left-grouping", "value"),
			),
		)
		async def update_customer_insights_left_results(date_from, date_to):
			# grouping_key, main_value = grouping_select.split(":")
			# return await self.update_customer_insights_results(date_from, date_to, grouping_key, main_value, None)
			return await self.update_customer_insights_results(date_from, date_to, 'chip_group', 'Online', 'all')

		# FIXME: update customers insights section (right)
		# @self.register_callback(
		# 	background=True,
		# 	output=(dash.Output("customer-insights-right-results", "children")),
		# 	inputs=(
		# 			dash.Input("filter-date-from", "value"),
		# 			dash.Input("filter-date-to", "value"),
		# 			dash.Input("customer-insights-right-grouping", "value"),
		# 	),
		# )
		# async def update_customer_insights_left_results(date_from, date_to, grouping_select):
		# 	return await self.update_customer_insights_results(date_from, date_to, grouping_select)

		# FIXME: update orders insights section
		@self.register_callback(
			background=True,
			output=(dash.Output("order-insights-section", "children")),
			inputs=(
					dash.Input(component_id="filter-date-from", component_property="value"),
					dash.Input(component_id="filter-date-to", component_property="value"),
			),
		)
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
													c="blue",
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

		# FIXME: update time series section
		@self.register_callback(
			background=True,
			output=(dash.Output("time-series-line-chart", "children")),
			inputs=(
					dash.Input("filter-date-from", "value"),
					dash.Input("filter-date-to", "value"),
					dash.State("order-insights-section-tabs", "value"),
					dash.Input("include-vip-toggle", "checked")
			),
		)
		async def update_time_series_section(date_from, date_to, tab, include_vip):
			results = await self.query_manager.execute_queries(
				query_names=[
					"event_entry_timeline",
					"time_series",
				],
				parameters={
					"date_from": dateutil.parser.parse(date_from),
					"date_to": dateutil.parser.parse(date_to)
				}
			)
			time_series_data = results['time_series'].to_dict(orient='records')
			event_entry_timeline = results['event_entry_timeline']

			# Prepare input data
			input_data = []
			for row in time_series_data:
				input_data.append(
					{
						"hour": row['hour'],
						"amount": row['regular_sales_amount'] + row['vip_sales_amount'] if include_vip else row['regular_sales_amount'],
						"count": row['regular_sales_count'] + row['vip_sales_count'] if include_vip else row['regular_sales_count'],
					}
				)
			return [
				dmc.LineChart(
					h=300,
					dataKey="hour",
					data=input_data,
					curveType="bump",
					# withRightYAxis=True,
					yAxisLabel="Amount",
					# rightYAxisLabel="Count",
					series=[
						{ "name": "amount", "label": "Sales Value", "color": "blue" },
						# { "name": "count", "label": "Orders", "color": "gray", "yAxisId": "right" }
					],
					referenceLines=[
						*[{
							"x": row['start_time'],
							"label": row['entry_name'],
							"labelPosition": "middle",
							"color": "gray",
						} for _, row in event_entry_timeline.iterrows() if row['stage_name'] is None]
					],
					yAxisProps={ "width": 80 },
					withLegend=True,
				),
			]

		# FIXME: update cash flow section
		@self.register_callback(
			background=True,
			output=(dash.Output("cash-flow-section", "children")),
			inputs=(
					dash.Input("filter-date-from", "value"),
					dash.Input("filter-date-to", "value"),
					dash.State("order-insights-section-tabs", "value"),
			),
		)
		async def update_cash_flow_section(date_from, date_to, tab):
			results = await self.query_manager.execute_queries(
				query_names=[
					"sankey_diagram"
				],
				parameters={
					"date_from": dateutil.parser.parse(date_from),
					"date_to": dateutil.parser.parse(date_to)
				}
			)
			sankey_data = results['sankey_diagram']

			diagram = SankeyDiagram()

			# Add nodes
			diagram.add_node('online_topup', 'Online top-up', x=0.05, y=-0.2, color='indigo')
			diagram.add_node('card_topup', 'Card top-up', x=0.05, y=0.2, color='cool_gray')
			diagram.add_node('cash_topup', 'Cash top-up', x=0.05, y=0.4, color='cool_gray')
			diagram.add_node('vip_topup', 'VIP top-up', x=0.05, y=0.6, color='warm_gray')

			diagram.add_node('chip_payments', 'Chip payments', x=0.2, y=0.4, color='slate_blue')
			diagram.add_node('cash_card_payments', 'Cash/Card payments', x=0.2, y=0.6, color='light_steel')

			diagram.add_node('event_finances', 'Event finances', x=0.4, y=0.5, color='warm_gray')

			diagram.add_node('vendor_sales', 'Vendor sales', x=0.65, y=0.3, color='dusty_blue')
			# diagram.add_node('beer_sales', 'Beer', x=0.6, y=0, color='light_steel')
			# diagram.add_node('spirits_sales', 'Spirits', x=0.6, y=0, color='light_steel')
			# diagram.add_node('salty_sales', 'Salty', x=0.6, y=0, color='light_steel')
			# diagram.add_node('other_sales', 'Other', x=0.6, y=0, color='light_steel')
			# diagram.add_node('non_alcoholic_sales', 'Non-alcoholic', x=0.6, y=0, color='light_steel')
			# diagram.add_node('wine_sales', 'Wine', x=0.6, y=0, color='light_steel')
			# diagram.add_node('complimentary_sales', 'Complimentary', x=0.6, y=0, color='light_steel'),
			# diagram.add_node('sweet_sales', 'Sweet', x=0.6, y=0, color='light_steel')

			diagram.add_node('unused_credit', 'Unused credit', x=0.6, y=0.8, color='peach')

			diagram.add_node('organizer_commission', 'Organizer commission', x=0.8, y=0.65, color='sage')

			diagram.add_node('sellers_payout', 'Sellers payout', x=0.8, y=0.2, color='mint')
			diagram.add_node('organizer_revenue', 'Organizer revenue', x=0.99, y=0.7, color='lavender')
			diagram.add_node('refunded', 'Refunded to the visitors', x=0.8, y=0.85, color='rose')

			# Add flows
			diagram.add_flow('online_topup', 'chip_payments', sankey_data['online_topup_amount'] / 100, color=None)
			diagram.add_flow('card_topup', 'chip_payments', sankey_data['card_topup_amount'] / 100, color=None)
			diagram.add_flow('cash_topup', 'chip_payments', sankey_data['cash_topup_amount'] / 100, color=None)
			diagram.add_flow('vip_topup', 'chip_payments', sankey_data['vip_topup_amount'] / 100, color=None)

			diagram.add_flow('chip_payments', 'event_finances', sankey_data['total_topup_amount'] / 100, color=None)
			diagram.add_flow('cash_card_payments', 'event_finances', sankey_data['non_chip_sales'] / 100, color=None)

			diagram.add_flow('event_finances', 'vendor_sales', sankey_data['vendor_sales'] / 100, color=None)
			# diagram.add_flow('event_finances', 'non_alcoholic_sales', sankey_data['non_alcoholic_sales'] / 100, color=None)
			# diagram.add_flow('event_finances', 'beer_sales', sankey_data['beer_sales'] / 100, color=None)
			# diagram.add_flow('event_finances', 'wine_sales', sankey_data['wine_sales'] / 100, color=None)
			# diagram.add_flow('event_finances', 'spirits_sales', sankey_data['spirits_sales'] / 100, color=None)
			# diagram.add_flow('event_finances', 'salty_sales', sankey_data['salty_sales'] / 100, color=None)
			# diagram.add_flow('event_finances', 'sweet_sales', sankey_data['sweet_sales'] / 100, color=None)
			# diagram.add_flow('event_finances', 'complimentary_sales', sankey_data['complimentary_sales'] / 100, color=None)
			# diagram.add_flow('event_finances', 'other_sales', sankey_data['other_sales'] / 100, color=None)

			# diagram.add_flow('non_alcoholic_sales', 'vendor_sales', sankey_data['non_alcoholic_sales'] / 100, color=None)
			# diagram.add_flow('beer_sales', 'vendor_sales', sankey_data['beer_sales'] / 100, color=None)
			# diagram.add_flow('wine_sales', 'vendor_sales', sankey_data['wine_sales'] / 100, color=None)
			# diagram.add_flow('spirits_sales', 'vendor_sales', sankey_data['spirits_sales'] / 100, color=None)
			# diagram.add_flow('salty_sales', 'vendor_sales', sankey_data['salty_sales'] / 100, color=None)
			# diagram.add_flow('sweet_sales', 'vendor_sales', sankey_data['sweet_sales'] / 100, color=None)
			# diagram.add_flow('complimentary_sales', 'vendor_sales', sankey_data['complimentary_sales'] / 100, color=None)
			# diagram.add_flow('other_sales', 'vendor_sales', sankey_data['other_sales'] / 100, color=None)

			diagram.add_flow('event_finances', 'unused_credit', sankey_data['unused_credits'] / 100, color=None)

			diagram.add_flow('vendor_sales', 'sellers_payout', sankey_data['to_be_forwarded'] / 100, color=None)
			diagram.add_flow('vendor_sales', 'organizer_commission', sankey_data['organizer_commission'] / 100, color=None)

			diagram.add_flow('unused_credit', 'refunded', sankey_data['refunded_to_visitors'] / 100, color=None)
			diagram.add_flow('unused_credit', 'organizer_revenue', sankey_data['non_refunded_credits'] / 100, color=None)
			diagram.add_flow('organizer_commission', 'organizer_revenue', sankey_data['organizer_commission'] / 100, color=None)

			# Create the figure
			fig = go.Figure(
				data=[go.Sankey(
					arrangement='snap',
					**diagram.to_plotly()
				)]
			)

			# Update layout
			fig.update_layout(
				title=dict(text="Cash Flow Diagram", x=0.5, xanchor='center'),
				font_size=12,
				height=600,
				width=1200,
				margin=dict(l=50, r=50, t=50, b=50),
				plot_bgcolor='rgba(0,0,0,0)',
				paper_bgcolor='rgba(0,0,0,0)'
			)

			return [
				dmc.GridCol(
					span=12,
					children=[
						dmc.Card(
							withBorder=True,
							children=[dcc.Graph(id="sankey-chart", figure=fig)]
						)
					]
				)
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
