from __future__ import annotations

import datetime

import dash as dash
import dash_ag_grid as dag
import dash_mantine_components as dmc
from dash import dcc, html
from dash_iconify import DashIconify

from dashboard_app._db_utils import QueryDefinition, QueryManager, QueryParameter
from dashboard_app._format_utils import format_event_datetime, format_number, interpolated_text_with_components, locale_cs_d3, parse_date, to_timestamp


def performance_section_children(app):
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
								children=DashIconify(icon="icon-park-outline:analysis", width=25)
							),
							html.Div(
								children=[
									dmc.Title(
										size="1.25rem",
										children='Performance Analysis'
									),
									dmc.Text(
										"Analyze transactional behavior over time",
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
				p="sm",
				grow=False,
				id="kpi-cards-section",
				children=[
					# total customers
					dmc.GridCol(
						span=4,
						className="with-loading",
						children=[
							dcc.Loading(
								type="dot",
								target_components={ "total-customers-card": "children" },
								id="total-customers-card"
							),
						]
					),
					# total processed
					dmc.GridCol(
						span=4,
						className="with-loading",
						children=[
							dcc.Loading(
								type="dot",
								target_components={ "total-transactions-card": "children" },
								id="total-transactions-card"
							),
						]
					),
					# volume peaks
					dmc.GridCol(
						span=4,
						className="with-loading",
						children=[
							dcc.Loading(
								type="dot",
								target_components={ "transaction-volume-peak-card": "children" },
								id="transaction-volume-peak-card"
							),
						],
					),
					# time series chart
					dmc.GridCol(
						span=12,
						children=[
							dmc.Card(
								withBorder=True,
								children=[
									dmc.Grid(
										children=[
											# chart
											dmc.GridCol(
												span=9,
												className="!pt-6",
												children=[
													dcc.Loading(
														type="dot",
														target_components={ "performance-time-series-chart": "children" },
														children=[html.Div(id="performance-time-series-chart")],
													),
												]
											),
											# control panel
											dmc.GridCol(
												span=3,
												className="flex flex-col",
												children=[
													dmc.Card(
														p="sm",
														className="bg-zinc-50 grow",
														children=[
															dmc.Stack(
																gap="sm",
																children=[
																	dmc.Stack(
																		gap="xs",
																		children=[
																			dmc.Text(
																				"Chart control panel",
																				size="sm",
																				fw=600
																			),
																			dmc.Text(
																				"Filter transactions by date range, type, metric, and granularity",
																				c="dimmed",
																				size="sm",
																			),
																		],
																	),
																	# transaction type select
																	dmc.Select(
																		id="filter-transaction-type",
																		label="Transaction type",
																		value="all",
																		data=[
																			{ 'value': 'all', 'label': 'All transactions' },
																			{ 'value': 'order', 'label': 'Orders' },
																			{ 'value': 'top-up', 'label': 'Top-ups' },
																			{ 'value': 'check-in', 'label': 'Check-ins', 'disabled': True },
																		],
																	),
																	# metric value select
																	dmc.Stack(
																		gap=0,
																		children=[
																			dmc.Text(
																				"Metric",
																				size="sm",
																				fw="500",
																				mb=0
																			),
																			dmc.SegmentedControl(
																				id="filter-metric",
																				value="count",
																				data=[
																					{ 'value': 'count', 'label': 'Count' },
																					{ 'value': 'sum', 'label': 'Sum' },
																					{ 'value': 'commission', 'label': 'Commission' },
																				],
																			),
																		]
																	),
																	# granularity select
																	dmc.Select(
																		id="filter-granularity",
																		label="Granularity",
																		value="60",
																		data=[
																			{ 'value': '1', 'label': 'Minute' },
																			{ 'value': '15', 'label': '15 Minutes' },
																			{ 'value': '30', 'label': '30 Minutes' },
																			{ 'value': '60', 'label': 'Hour' },
																			{ 'value': '1440', 'label': 'Day' },
																		],
																	),
																]
															)
														]
													)
												]
											),
										],
									)
								]
							)
						]
					),
					dmc.GridCol(
						children=[
							dmc.Tabs(
								orientation="vertical",
								variant="outline",
								value="sale-points",
								children=[
									dmc.TabsList(
										[
											dmc.TabsTab("Sale Places", value="sale-points"),
											dmc.TabsTab("Top-Up Points", value="topup-points"),
											dmc.TabsTab("Vendors", value="vendors"),
											dmc.TabsTab("Products", value="products"),
										]
									),
									# sale places
									dmc.TabsPanel(
										value="sale-points",
										className="p-2 border border-l-0 border-zinc-200",
										children=[
											dag.AgGrid(
												id="performance-selling-places",
												columnDefs=[
													{ 'headerName': 'Selling place', 'field': 'entity' },
													{ 'headerName': 'Trx processed', 'field': 'transaction_count', 'type': 'numericColumn', "valueFormatter": { "function": f"{locale_cs_d3}.format(',.0f')(params.value)" } },
													{ 'headerName': 'Customers processed', 'field': 'customer_count', 'type': 'numericColumn', "valueFormatter": { "function": f"{locale_cs_d3}.format(',.0f')(params.value)" } },
													{ 'headerName': 'Max hourly peak', 'field': 'max_hourly_peak', 'type': 'numericColumn', "valueFormatter": { "function": f"{locale_cs_d3}.format(',.0f')(params.value)" } },
												],
												defaultColDef={ "resizable": True, "sortable": True, "filter": True },
												columnSize="responsiveSizeToFit",
											)
										]
									),
									# top-up points
									dmc.TabsPanel(
										value="topup-points",
										className="p-2 border border-l-0 border-zinc-200",
										children=[
											dag.AgGrid(
												id="performance-topup-places",
												columnDefs=[
													{ 'headerName': 'Top-up point', 'field': 'entity' },
													{ 'headerName': 'Trx processed', 'field': 'transaction_count', 'type': 'numericColumn', "valueFormatter": { "function": f"{locale_cs_d3}.format(',.0f')(params.value)" } },
													{ 'headerName': 'Customers processed', 'field': 'customer_count', 'type': 'numericColumn', "valueFormatter": { "function": f"{locale_cs_d3}.format(',.0f')(params.value)" } },
													{ 'headerName': 'Max hourly peak', 'field': 'max_hourly_peak', 'type': 'numericColumn', "valueFormatter": { "function": f"{locale_cs_d3}.format(',.0f')(params.value)" } },
												],
												defaultColDef={ "resizable": True, "sortable": True, "filter": True },
												columnSize="responsiveSizeToFit",
											)]
									),
									# vendors
									dmc.TabsPanel(
										value="vendors",
										className="p-2 border border-l-0 border-zinc-200",
										children=[
											dag.AgGrid(
												id="performance-vendors",
												columnDefs=[
													{ 'headerName': 'Vendor', 'field': 'legal_name' },
													{ 'headerName': 'Trx processed', 'field': 'transaction_count', 'type': 'numericColumn', "valueFormatter": { "function": f"{locale_cs_d3}.format(',.0f')(params.value)" } },
													{ 'headerName': 'Customers processed', 'field': 'customer_count', 'type': 'numericColumn', "valueFormatter": { "function": f"{locale_cs_d3}.format(',.0f')(params.value)" } },
												],
												defaultColDef={ "resizable": True, "sortable": True, "filter": True },
												columnSize="responsiveSizeToFit",
											)]
									),
									# products
									dmc.TabsPanel(
										value="products",
										className="p-2 border border-l-0 border-zinc-200",
										children=[
											dag.AgGrid(
												id="performance-products",
												columnDefs=[
													{ 'headerName': 'Product', 'field': 'product_name' },
													{ 'headerName': 'Sales count', 'field': 'sales_count', 'type': 'numericColumn', "valueFormatter": { "function": f"{locale_cs_d3}.format(',.0f')(params.value)" } },
													{ 'headerName': 'Refunds count', 'field': 'refund_count', 'type': 'numericColumn', "valueFormatter": { "function": f"{locale_cs_d3}.format(',.0f')(params.value)" } },
													{ 'headerName': 'Customers processed', 'field': 'customer_count', 'type': 'numericColumn', "valueFormatter": { "function": f"{locale_cs_d3}.format(',.0f')(params.value)" } },
												],
												defaultColDef={ "resizable": True, "sortable": True, "filter": True },
												columnSize="responsiveSizeToFit",
											)
										]
									),
								],
							)
						]
					),
				]
			),
		],
	)


def performance_section_callbacks(app):
	# update time series section
	@app.register_callback(
		background=True,
		output=(dash.Output("performance-time-series-chart", "children")),
		inputs=(
				dash.Input("filter-date-from", "value"),
				dash.Input("filter-date-to", "value"),
				dash.Input("filter-transaction-type", "value"),
				dash.Input("filter-metric", "value"),
				dash.Input("filter-granularity", "value"),
		),
	)
	async def update_performance_time_series_section(date_from, date_to, transaction_type, metric, granularity):
		results = await app.query_manager.execute_queries(
			query_names=[
				# TODO: when time improve (add chip registers and time processing stats)
				"time_series",
				"event_entry_timeline",
			],
			parameters={
				"date_from": parse_date(date_from),
				"date_to": parse_date(date_to),
				"granularity_minutes": int(granularity),
				# when daily, start at 6am (4 UTC + 2 CEST), timezones go brr
				"day_start_hour": int(4),
			}
		)
		time_series_data = results['time_series'].to_dict(orient='records')
		event_entry_timeline = results['event_entry_timeline']

		def get_row_data(rd):
			if transaction_type == "all":
				return {
					"count": rd['transaction_count'],
					"sum": rd['transaction_sum'],
					"commission": rd['org_comm'],
				}[metric]

			if transaction_type == "order":
				return {
					"count": rd['regular_order_count'] + rd['vip_order_count'],
					"sum": rd['regular_order_amount'] + rd['vip_order_amount'],
					"commission": rd['org_comm'],
				}[metric]

			if transaction_type == "top-up":
				return {
					"count": rd['topup_count'] + rd['vip_topup_count'],
					"sum": rd['topup_amount'] + rd['vip_topup_amount'],
					"commission": 0,
				}[metric]

			# TODO: check-ins (chip registers)

			return {
				"count": 0,
				"sum": 0,
				"commission": 0,
			}[metric]

		# Prepare input data
		input_data = []
		for row in time_series_data:
			input_data.append(
				{
					"slot_start": to_timestamp(row['slot_start']),
					"value": get_row_data(row),
				}
			)
		# Get visible program timeline
		program_timeline = event_entry_timeline[(
			# or stage_name is None
				event_entry_timeline['stage_name'].isnull()
				# if stage_name include "Jihlava"
				| event_entry_timeline['stage_name'].str.contains("Jihlava")
		)]
		# Fill in the slots for reference lines
		# for row in program_timeline.itertuples():
		# 	input_data.append(
		# 		{
		# 			"slot_start": to_timestamp(row.start_time),
		# 			"value": 0,
		# 		}
		# 	)
		# Prepare reference lines
		reference_lines = [
			{
				"x": to_timestamp(row.start_time),
				"label": row.entry_name,
				"labelPosition": "top",
				"color": "gray" if row.stage_name is None else "indigo",
				# "ifOverflow": "extendDomain",
			} for row in program_timeline.itertuples()
		]

		# Format the slot_start with format_event_datetime() method
		input_data = sorted(input_data, key=lambda x: x['slot_start'])
		for row in input_data:
			# row['slot_start'] = format_event_datetime(row['slot_start'], True)
			row['slot_start'] = to_timestamp(row['slot_start']).strftime("%H:%M")
		# Sort input data and reference lines
		# reference_lines = sorted(reference_lines, key=lambda x: x['x'])
		# reference_lines = [
		# 	{
		# 		"label": "Day 1",
		# 		"labelPosition": "top",
		# 		"color": "gray",
		# 		"x": to_timestamp("2024-07-04T00:00:00")
		# 	}
		# ]

		# TODO: create plotly bar chart instead?

		# TODO
		return [
			dmc.AreaChart(
				h=300,
				dataKey="slot_start",
				data=input_data,
				curveType="bump",
				yAxisLabel="Amount",
				withGradient=True,
				withDots=False,
				# withRightYAxis=True,
				# rightYAxisLabel="Count",
				xAxisProps={ "tickMargin": 50, "orientation": "bottom" },
				series=[
					{ "name": "value", "label": metric, "color": "green" },
				],
				referenceLines=reference_lines,
				yAxisProps={ "width": 80 },
			)
		]

	# TODO: maybe move to customer analysis later
	# update customers per days
	@app.register_callback(
		background=True,
		output=(dash.Output("total-customers-card", "children")),
		inputs=(
				dash.Input("filter-date-from", "value"),
				dash.Input("filter-date-to", "value"),
		),
	)
	async def update_customers_per_day_card(date_from, date_to):
		results = await app.query_manager.execute_queries(
			query_names=[
				"customers_per_day",
				"total_active"
			],
			or_query_defs={
				'customers_per_day': QueryDefinition(
					name="customers_per_day",
					sql=QueryManager.process_sql_query(
						"""
							SELECT * FROM customer_an_attendance(:date_from$1, :date_to$2)
							ORDER BY active_chips DESC;
						"""
					),
					parameters=[
						QueryParameter("date_from", datetime.datetime),
						QueryParameter("date_to", datetime.datetime)
					],
					default_data="FSCacheDefault"
				),
				'total_active': QueryDefinition(
					name="total_active",
					sql=QueryManager.process_sql_query(
						"""
						SELECT
							MAX(total_chips) as total_active
						FROM customer_an_attendance(:date_from$1, :date_to$2)
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
		customers_per_day = results['customers_per_day']
		most_active_day = customers_per_day.iloc[0]
		total_active = results['total_active'].iloc[0]['total_active']

		return dmc.Card(
			className="h-full",
			p="sm",
			withBorder=True,
			children=[
				dmc.Stack(
					gap="xs",
					className="grow",
					children=[
						dmc.Text("Active customers", size="sm", fw=500),
						dmc.Group(
							gap="xs",
							justify="space-between",
							children=[
								dmc.Text(
									f"{format_number(total_active)} customers",
									size="xl",
									fw=700
								),
								dmc.ThemeIcon(
									size="lg",
									radius="xl",
									color="green",
									variant="light",
									children=DashIconify(icon="mdi:user", width=20)
								),
							]
						),
						dmc.Text(
							interpolated_text_with_components(
								"was the total number of active customers at the event",
								{ }
							),
							size="sm",
							className="mt-auto",
							c="dimmed"
						),
						dmc.Divider(),
						dmc.Group(
							gap="xs",
							justify="space-between",
							children=[
								dmc.Text(
									f"With the most of {format_number(most_active_day['active_chips'])} active",
									size="sm",
									fw=500
								),
								dmc.Text(
									f"on {format_event_datetime(most_active_day['day'], False)}",
									size="sm",
									c="dimmed"
								),
							]
						),
					]
				)
			]
		)

	# update total transactions card
	@app.register_callback(
		background=True,
		output=(dash.Output("total-transactions-card", "children")),
		inputs=(
				dash.Input("filter-date-from", "value"),
				dash.Input("filter-date-to", "value"),
		),
	)
	async def update_total_transactions_card(date_from, date_to):
		results = await app.query_manager.execute_queries(
			query_names=[
				"total_transactions"
			],
			or_query_defs={
				'total_transactions': QueryDefinition(
					name="total_transactions",
					sql=QueryManager.process_sql_query(
						"""
						SELECT
							SUM(t.count) as count
						FROM performance_an_transaction_processing_hourly(:date_from$1, :date_to$2) t;
						"""
					),
					parameters=[
						QueryParameter("date_from", datetime.datetime),
						QueryParameter("date_to", datetime.datetime)
					],
					default_data="FSCacheDefault",
				),
			},
			parameters={
				"date_from": parse_date(date_from),
				"date_to": parse_date(date_to),
			}
		)
		total_transactions = results['total_transactions'].iloc[0]['count']

		return dmc.Card(
			className="h-full",
			p="sm",
			withBorder=True,
			children=[
				dmc.Stack(
					gap="xs",
					className="grow",
					children=[
						dmc.Text("Processed transactions", size="sm", fw=500),
						dmc.Group(
							gap="xs",
							justify="space-between",
							children=[
								dmc.Text(
									f"{format_number(total_transactions)} transactions",
									size="xl",
									fw=700
								),
								dmc.ThemeIcon(
									size="lg",
									radius="xl",
									color="green",
									variant="light",
									children=DashIconify(icon="grommet-icons:transaction", width=20)
								),
							]
						),
						dmc.Text(
							interpolated_text_with_components(
								"were processed at the event",
								{ }
							),
							size="sm",
							className="mt-auto",
							c="dimmed"
						),
					]
				)
			]
		)

	# update transaction volume peak card
	@app.register_callback(
		background=True,
		output=(dash.Output("transaction-volume-peak-card", "children")),
		inputs=(
				dash.Input("filter-date-from", "value"),
				dash.Input("filter-date-to", "value"),
		),
	)
	async def update_transaction_volume_peak_card(date_from, date_to):
		results = await app.query_manager.execute_queries(
			query_names=[
				"transaction_volume_peak"
			],
			or_query_defs={
				'transaction_volume_peak': QueryDefinition(
					name="transaction_volume_peak",
					sql=QueryManager.process_sql_query(
						"""
						SELECT
							t.hour,
							SUM(t.count) as count
						FROM performance_an_transaction_processing_hourly(:date_from$1, :date_to$2) t
						GROUP BY t.hour
						ORDER BY count DESC
						LIMIT 1;
						"""
					),
					parameters=[
						QueryParameter("date_from", datetime.datetime),
						QueryParameter("date_to", datetime.datetime)
					],
					default_data="FSCacheDefault",
				),
			},
			parameters={
				"date_from": parse_date(date_from),
				"date_to": parse_date(date_to),
			}
		)
		transaction_volume_peak = results['transaction_volume_peak'].iloc[0]

		return dmc.Card(
			className="h-full",
			p="sm",
			withBorder=True,
			children=[
				dmc.Stack(
					gap="xs",
					className="grow",
					children=[
						dmc.Text("Volume peaks", size="sm", fw=500),
						dmc.Group(
							gap="xs",
							justify="space-between",
							children=[
								dmc.Text(
									f"{format_number(transaction_volume_peak['count'])} transactions per hour",
									size="xl",
									fw=700
								),
								dmc.ThemeIcon(
									size="lg",
									radius="xl",
									color="green",
									variant="light",
									children=DashIconify(icon="material-symbols:speed", width=20)
								),
							]
						),
						dmc.Text(
							interpolated_text_with_components(
								"was the highest peak on {date}",
								{
									"date": format_event_datetime(transaction_volume_peak['hour'], True)
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

	# update top sale places table
	@app.register_callback(
		background=True,
		output=(dash.Output("performance-selling-places", "rowData")),
		inputs=(
				dash.Input("filter-date-from", "value"),
				dash.Input("filter-date-to", "value"),
		),
	)
	async def update_top_selling_places_table(date_from, date_to):
		results = await app.query_manager.execute_queries(
			query_names=[
				"top_selling_places"
			],
			or_query_defs={
				'top_selling_places': QueryDefinition(
					name="top_selling_places",
					sql=QueryManager.process_sql_query(
						"""
						SELECT * FROM performance_an_best_sale_places(:date_from$1, :date_to$2)
						LIMIT 10
						"""
					),
					parameters=[
						QueryParameter("date_from", datetime.datetime),
						QueryParameter("date_to", datetime.datetime)
					],
					default_data="FSCacheDefault",
				),
			},
			parameters={
				"date_from": parse_date(date_from),
				"date_to": parse_date(date_to),
			}
		)
		top_places = results['top_selling_places']

		return top_places.to_dict(orient='records')

	# update top topup places table
	@app.register_callback(
		background=True,
		output=(dash.Output("performance-topup-places", "rowData")),
		inputs=(
				dash.Input("filter-date-from", "value"),
				dash.Input("filter-date-to", "value"),
		),
	)
	async def update_top_topup_places_table(date_from, date_to):
		results = await app.query_manager.execute_queries(
			query_names=[
				"top_topup_places"
			],
			or_query_defs={
				'top_topup_places': QueryDefinition(
					name="top_topup_places",
					sql=QueryManager.process_sql_query(
						"""
						SELECT * FROM performance_an_best_topup_points(:date_from$1, :date_to$2)
						LIMIT 10
						"""
					),
					parameters=[
						QueryParameter("date_from", datetime.datetime),
						QueryParameter("date_to", datetime.datetime)
					],
					default_data="FSCacheDefault",
				),
			},
			parameters={
				"date_from": parse_date(date_from),
				"date_to": parse_date(date_to),
			}
		)
		top_places = results['top_topup_places']

		return top_places.to_dict(orient='records')

	# update top vendors table
	@app.register_callback(
		background=True,
		output=(dash.Output("performance-vendors", "rowData")),
		inputs=(
				dash.Input("filter-date-from", "value"),
				dash.Input("filter-date-to", "value"),
		),
	)
	async def update_top_vendors_table(date_from, date_to):
		results = await app.query_manager.execute_queries(
			query_names=[
				"top_vendors"
			],
			or_query_defs={
				'top_vendors': QueryDefinition(
					name="top_vendors",
					sql=QueryManager.process_sql_query(
						"""
						SELECT * FROM performance_an_best_vendors(:date_from$1, :date_to$2)
						LIMIT 10
						"""
					),
					parameters=[
						QueryParameter("date_from", datetime.datetime),
						QueryParameter("date_to", datetime.datetime)
					],
					default_data="FSCacheDefault",
				),
			},
			parameters={
				"date_from": parse_date(date_from),
				"date_to": parse_date(date_to),
			}
		)
		top_vendors = results['top_vendors']

		return top_vendors.to_dict(orient='records')

	# update top products table
	@app.register_callback(
		background=True,
		output=(dash.Output("performance-products", "rowData")),
		inputs=(
				dash.Input("filter-date-from", "value"),
				dash.Input("filter-date-to", "value"),
		),
	)
	async def update_top_products_table(date_from, date_to):
		results = await app.query_manager.execute_queries(
			query_names=[
				"top_products"
			],
			or_query_defs={
				'top_products': QueryDefinition(
					name="top_products",
					sql=QueryManager.process_sql_query(
						"""
						SELECT * FROM performance_an_best_products(:date_from$1, :date_to$2)
						LIMIT 10
						"""
					),
					parameters=[
						QueryParameter("date_from", datetime.datetime),
						QueryParameter("date_to", datetime.datetime)
					],
					default_data="FSCacheDefault",
				),
			},
			parameters={
				"date_from": parse_date(date_from),
				"date_to": parse_date(date_to),
			}
		)
		top_products = results['top_products']

		return top_products.to_dict(orient='records')
