from __future__ import annotations

import asyncio
import datetime
from uuid import uuid4

import dash as dash
import dash_mantine_components as dmc
import dateutil as dateutil
import diskcache
import pandas as pd
import plotly.graph_objects as go
from dash import dcc, html
from dash_iconify import DashIconify

from db_queries import query_manager
from db_utils import format_number, format_number_short, format_price
from chart_utils import SankeyDiagram, SankeyFlow, SankeyNode, get_color
from dash_utils import index_string, background_callback_manager, launch_uid, external_script

# set the React version
dash._dash_renderer._set_react_version("18.2.0")

# (day starts at 06:00am, day ends 05:59am +1 next day)
days = {
	'1': ('2024-07-04 06:00:00', '2024-07-05 05:59:59'),
	'2': ('2024-07-05 06:00:00', '2024-07-06 05:59:59'),
	'3': ('2024-07-06 06:00:00', '2024-07-07 05:59:59'),
}


# ---- Dash Application ----
class MainApplication:
	def __init__(self):

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

	def register_callback(self, output, inputs, prevent_initial_call=False, background=False):
		"""
		Decorator for Dash callbacks that handles async operations and error handling.

		Args:
				output: Dash Output or tuple of Outputs
				inputs: Dash Input or tuple of Inputs
				prevent_initial_call: Boolean to prevent initial callback
				background: Boolean to run callback in background
		"""

		def decorator(func):
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
			wrapped = self.__app.callback(
				output=output,
				inputs=inputs,
				prevent_initial_call=prevent_initial_call,
				background=background,
				manager=background_callback_manager
			)(async_callback_wrapper if background else sync_callback_wrapper)

			return wrapped

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
							# Main content
							html.Main(
								className="grid grid-cols-1 gap-4",
								children=[
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
											# Main overview section
											dcc.Loading(
												type="dot",
												target_components={ "orders-insights-section": "children" },
												children=[
													dmc.Grid(
														id="orders-insights-section",
														gutter="md",
														p="sm",
														grow=False,
														children=[]
													)
												],
											),
											# Content tabs
											dmc.Tabs(
												id="tabs",
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

	def _register_callbacks(self):
		# sync date preset with date inputs
		@self.register_callback(
			output=(dash.Output("filter-date-from", "value"), dash.Output("filter-date-to", "value")),
			inputs=(dash.Input("filter-date-preset", "value")),
		)
		def sync_date_preset(preset):
			return days[preset] if preset in days else (days['1'][0], days['3'][1])

		# FIXME: update orders insights section
		@self.register_callback(
			background=True,
			output=(dash.Output("orders-insights-section", "children")),
			inputs=(dash.Input("filter-date-from", "value"), dash.Input("filter-date-to", "value")),
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
					dash.State("tabs", "value"),
					dash.Input("include-vip-toggle", "checked")
			),
		)
		async def update_time_series_section(date_from, date_to, current_tab, include_vip):
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
					dash.State("tabs", "value"),
			),
		)
		async def update_cash_flow_section(date_from, date_to, current_tab):
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

			diagram.add_node('vendor_sales', 'Vendor sales', x=0.6, y=0.3, color='dusty_blue')
			diagram.add_node('unused_credit', 'Unused credit', x=0.6, y=0.85, color='peach')

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

	@property
	def app(self):
		return self.__app


# Run the app
if __name__ == '__main__':
	Application = MainApplication()
	app = Application.app
	app.run_server(debug=True, port=4001)
# app.run_server(debug=False, host='192.168.0.167', port=4000)
