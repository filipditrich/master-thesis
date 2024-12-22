from __future__ import annotations

import datetime

import dash as dash
import dash_ag_grid as dag
import dash_mantine_components as dmc
import dateutil as dateutil
from dash import dcc, html
from dash_iconify import DashIconify
from pandas import Timestamp

from db_utils import QueryDefinition, QueryManager, QueryParameter, format_date, format_number, interpolated_text_with_components, locale_cs_d3


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
						id='total-customers-card',
					),
					# TODO: total processed
					dmc.GridCol(
						span=4,
						id='total-transactions-card'
					),
					# TODO: volume peaks
					dmc.GridCol(
						span=4,
						id='transaction-volume-peak-card',
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
					# TODO: top selling places table
					dmc.GridCol(
						span=6,
						children=[
							dag.AgGrid(
								id="performance-selling-places",
								style={ "height": "264px" },
								columnDefs=[
									{ 'headerName': 'Selling place', 'field': 'place_name' },
									{ 'headerName': 'Count', 'field': 'count', 'type': 'numericColumn', "valueFormatter": { "function": f"{locale_cs_d3}.format(',.0f')(params.value)" } },
									{ 'headerName': 'Sum', 'field': 'sum', "valueFormatter": { "function": f"{locale_cs_d3}.format('($,.0f')(params.value/100)" }, 'type': 'numericColumn' },
									# { 'headerName': 'Commission', 'field': 'commission', "valueFormatter": { "function": f"{locale_cs_d3}.format('($,.0f')(params.value)" }, 'type': 'numericColumn' },
								],
								defaultColDef={ "resizable": True, "sortable": True, "filter": True },
								columnSize="sizeToFit",
							)
						]
					),
					# TODO: top top-up places table
					dmc.GridCol(
						span=6,
						children=[
							dag.AgGrid(
								id="performance-topup-places",
								style={ "height": "264px" },
								columnDefs=[
									{ 'headerName': 'Top-up point', 'field': 'place_name' },
									{ 'headerName': 'Count', 'field': 'count', 'type': 'numericColumn', "valueFormatter": { "function": f"{locale_cs_d3}.format(',.0f')(params.value)" } },
									{ 'headerName': 'Sum', 'field': 'sum', "valueFormatter": { "function": f"{locale_cs_d3}.format('($,.0f')(params.value/100)" }, 'type': 'numericColumn' },
									# { 'headerName': 'Commission', 'field': 'commission', "valueFormatter": { "function": f"{locale_cs_d3}.format('($,.0f')(params.value)" }, 'type': 'numericColumn' },
								],
								defaultColDef={ "resizable": True, "sortable": True, "filter": True },
								columnSize="sizeToFit",
							)
						]
					),
					# TODO: top vendors table
					dmc.GridCol(
						span=6,
						children=[
							dag.AgGrid(
								id="performance-vendors",
								style={ "height": "264px" },
								columnDefs=[
									{ 'headerName': 'Vendor', 'field': 'vendor_name' },
									{ 'headerName': 'Count', 'field': 'count', 'type': 'numericColumn', "valueFormatter": { "function": f"{locale_cs_d3}.format(',.0f')(params.value)" } },
									{ 'headerName': 'Sum', 'field': 'sum', "valueFormatter": { "function": f"{locale_cs_d3}.format('($,.0f')(params.value/100)" }, 'type': 'numericColumn' },
									# { 'headerName': 'Commission', 'field': 'commission', "valueFormatter": { "function": f"{locale_cs_d3}.format('($,.0f')(params.value)" }, 'type': 'numericColumn' },
								],
								defaultColDef={ "resizable": True, "sortable": True, "filter": True },
								columnSize="sizeToFit",
							)
						]
					),
					# TODO: top products table
					dmc.GridCol(
						span=6,
						children=[
							dag.AgGrid(
								id="performance-products",
								style={ "height": "264px" },
								columnDefs=[
									{ 'headerName': 'Product', 'field': 'product_name' },
									{ 'headerName': 'Count', 'field': 'count', 'type': 'numericColumn', "valueFormatter": { "function": f"{locale_cs_d3}.format(',.0f')(params.value)" } },
									{ 'headerName': 'Sum', 'field': 'sum', "valueFormatter": { "function": f"{locale_cs_d3}.format('($,.0f')(params.value/100)" }, 'type': 'numericColumn' },
									# { 'headerName': 'Commission', 'field': 'commission', "valueFormatter": { "function": f"{locale_cs_d3}.format('($,.0f')(params.value)" }, 'type': 'numericColumn' },
								],
								defaultColDef={ "resizable": True, "sortable": True, "filter": True },
								columnSize="sizeToFit",
							)
						]
					),
				]
			),
		],
	);


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
				"time_series",
				"event_entry_timeline",
			],
			parameters={
				"date_from": dateutil.parser.parse(date_from),
				"date_to": dateutil.parser.parse(date_to),
				"granularity_minutes": int(granularity),
				# when daily, start at 6am (4 UTC + 2 CEST) lmao timezones go brr
				"day_start_hour": int(4),
			}
		)
		time_series_data = results['time_series'].to_dict(orient='records')
		event_entry_timeline = results['event_entry_timeline']

		def to_timestamp(dt):
			# if dt is string
			if isinstance(dt, str):
				# return int(dateutil.parser.parse(dt).timestamp())
				return dateutil.parser.parse(dt);

			# if dt is Timestamp
			if isinstance(dt, Timestamp):
				# return int(dt.timestamp())
				return dt

			# if dt is int
			if isinstance(dt, int):
				# return dt
				return dateutil.parser.parse(str(dt))

			# if dt is something else
			print("to_timestamp: unknown type", type(dt))
			return dt

		def get_row_data(row):
			if transaction_type == "all":
				return {
					"count": row['transaction_count'],
					"sum": row['transaction_sum'],
					"commission": row['org_comm'],
				}[metric]

			if transaction_type == "order":
				return {
					"count": row['regular_order_count'] + row['vip_order_count'],
					"sum": row['regular_order_amount'] + row['vip_order_amount'],
					"commission": row['org_comm'],
				}[metric]

			if transaction_type == "top-up":
				return {
					"count": row['topup_count'] + row['vip_topup_count'],
					"sum": row['topup_amount'] + row['vip_topup_amount'],
					"commission": 0,
				}[metric]

			# TODO: check-ins

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

		# Sort input data and reference lines
		input_data = sorted(input_data, key=lambda x: x['slot_start'])
		reference_lines = sorted(reference_lines, key=lambda x: x['x'])

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
				series=[
					{ "name": "value", "label": metric, "color": "green" },
				],
				referenceLines=reference_lines,
				yAxisProps={ "width": 80 },
			)
		]

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
							SELECT
								DATE_TRUNC('day', t.created) AS day,
								COUNT(DISTINCT t.chip_id) AS active_chips
							FROM pos_transactions_rich t
							WHERE t.chip_id IS NOT NULL
							GROUP BY day
							ORDER BY active_chips DESC;
						"""
					),
					parameters=[],
					default_data="FSCacheDefault"
				),
				'total_active': QueryDefinition(
					name="total_active",
					sql=QueryManager.process_sql_query(
						"""
						SELECT
							COUNT(DISTINCT c.chip_id) AS total_active
						FROM get_chip_customers(:date_from$1, :date_to$2) c
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
				"date_from": dateutil.parser.parse(date_from),
				"date_to": dateutil.parser.parse(date_to),
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
									f"on {format_date(most_active_day['day'], False)}",
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
							COUNT(t.transaction_id) AS total_transactions
						FROM pos_transactions t
						WHERE t.created BETWEEN :date_from$1 AND :date_to$2
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
				"date_from": dateutil.parser.parse(date_from),
				"date_to": dateutil.parser.parse(date_to),
			}
		)
		total_transactions = results['total_transactions'].iloc[0]['total_transactions']

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
						dmc.Divider(),
						dmc.Group(
							gap="xs",
							justify="space-between",
							children=[
								dmc.Text(
									f"TODO",
									size="sm",
									fw=500
								),
								dmc.Text(
									"TODO",
									size="sm",
									c="dimmed"
								),
							]
						),
					]
				)
			]
		);

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
							DATE_TRUNC('minute', t.created) AS minute,
							COUNT(t.transaction_id) AS transaction_count
						FROM pos_transactions t
						WHERE t.created BETWEEN :date_from$1 AND :date_to$2
						GROUP BY minute
						ORDER BY transaction_count DESC
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
				"date_from": dateutil.parser.parse(date_from),
				"date_to": dateutil.parser.parse(date_to),
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
									f"{format_number(transaction_volume_peak['transaction_count'])} transactions per minute",
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
									"date": format_date(transaction_volume_peak['minute'], True)
								}
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
									f"TODO",
									size="sm",
									fw=500
								),
								dmc.Text(
									"TODO",
									size="sm",
									c="dimmed"
								),
							]
						),
					]
				)
			]
		)

	# update top selling places table
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
						SELECT
							t.place_name,
							COUNT(t.transaction_id) AS count,
							SUM(t.amount) AS sum,
							SUM(t.org_comm) AS commission
						FROM pos_transactions_rich t
						WHERE t.created BETWEEN :date_from$1 AND :date_to$2
						AND t.is_order IS TRUE
						GROUP BY t.place_name
						ORDER BY sum DESC
						LIMIT 5;
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
				"date_from": dateutil.parser.parse(date_from),
				"date_to": dateutil.parser.parse(date_to),
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
						SELECT
							t.place_name,
							COUNT(t.transaction_id) AS count,
							SUM(t.amount) AS sum,
							SUM(t.org_comm) AS commission
						FROM pos_transactions_rich t
						WHERE t.created BETWEEN :date_from$1 AND :date_to$2
						AND t.is_order IS FALSE
						GROUP BY t.place_name
						ORDER BY sum DESC
						LIMIT 5;
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
				"date_from": dateutil.parser.parse(date_from),
				"date_to": dateutil.parser.parse(date_to),
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
						SELECT
							o.vendor_name,
							COUNT(o.transaction_id) AS count,
							SUM(o.total_amount) AS sum,
							SUM(o.org_comm) AS commission
						FROM pos_order_products_rich o
						WHERE o.created BETWEEN :date_from$1 AND :date_to$2
						GROUP BY o.vendor_name
						ORDER BY sum DESC
						LIMIT 5;
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
				"date_from": dateutil.parser.parse(date_from),
				"date_to": dateutil.parser.parse(date_to),
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
						SELECT
							o.product_name,
							COUNT(o.transaction_id) AS count,
							SUM(o.total_amount) AS sum,
							SUM(o.org_comm) AS commission
						FROM pos_order_products_rich o
						WHERE o.created BETWEEN :date_from$1 AND :date_to$2
						GROUP BY o.product_name
						ORDER BY sum DESC
						LIMIT 5;
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
				"date_from": dateutil.parser.parse(date_from),
				"date_to": dateutil.parser.parse(date_to),
			}
		)
		top_products = results['top_products']

		return top_products.to_dict(orient='records')
