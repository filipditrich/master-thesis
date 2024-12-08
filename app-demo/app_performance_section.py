from __future__ import annotations

import dash as dash
import dash_mantine_components as dmc
import dash_ag_grid as dag
import dateutil as dateutil
from dash import dcc, html
from dash_iconify import DashIconify
from pandas import Timestamp
from db_utils import format_number, format_number_short, interpolated_text_with_components, locale_cs_d3


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
								color="red",
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
				children=[
					# TODO: total customers
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
											dmc.Text("Active customers", size="sm", fw=500),
											dmc.Group(
												gap="xs",
												justify="space-between",
												children=[
													dmc.Text(
														f"{format_number(10009)} customers",
														size="xl",
														fw=700
													),
													dmc.ThemeIcon(
														size="lg",
														radius="xl",
														color="red",
														variant="light",
														children=DashIconify(icon="mdi:user", width=20)
													),
												]
											),
											dmc.Text(
												interpolated_text_with_components(
													"was the total number of active customers at the event",
													{
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
														f"With total {format_number(8066)} customers",
														size="sm",
														fw=500
													),
													dmc.Text(
														"on the last day",
														size="sm",
														c="dimmed"
													),
												]
											),
										]
									)
								]
							)
						]
					),
					# TODO: total processed
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
											dmc.Text("Processed transactions", size="sm", fw=500),
											dmc.Group(
												gap="xs",
												justify="space-between",
												children=[
													dmc.Text(
														f"{format_number(128500)} transactions",
														size="xl",
														fw=700
													),
													dmc.ThemeIcon(
														size="lg",
														radius="xl",
														color="red",
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
							)
						]
					),
					# TODO: volume peaks
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
											dmc.Text("Volume peaks", size="sm", fw=500),
											dmc.Group(
												gap="xs",
												justify="space-between",
												children=[
													dmc.Text(
														f"{format_number(150)} transactions per minute",
														size="xl",
														fw=700
													),
													dmc.ThemeIcon(
														size="lg",
														radius="xl",
														color="red",
														variant="light",
														children=DashIconify(icon="material-symbols:speed", width=20)
													),
												]
											),
											dmc.Text(
												interpolated_text_with_components(
													"was the highest peak on the {day} day at roughly {time}",
													{
														"day": "third",
														"time": "18:35"
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
						]
					),
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
					# TODO: top places table
					dmc.GridCol(
						span=4,
						children=[
							dag.AgGrid(
								id="performance-places",
								style={ "height": "264px" },
								# TODO
								rowData=[{
									'place_name': "TODO Place " + str(i),
									'count': 0,
									'sum': 0,
									'commission': 0,
								} for i in range(5)],
								columnDefs=[
									{ 'headerName': 'Place', 'field': 'place_name' },
									{ 'headerName': 'Count', 'field': 'count', 'type': 'numericColumn' },
									{ 'headerName': 'Sum', 'field': 'sum', "valueFormatter": { "function": f"{locale_cs_d3}.format('($,.0f')(params.value)" }, 'type': 'numericColumn' },
									{ 'headerName': 'Commission', 'field': 'commission', "valueFormatter": { "function": f"{locale_cs_d3}.format('($,.0f')(params.value)" }, 'type': 'numericColumn' },
								],
								defaultColDef={ "resizable": True, "sortable": True, "filter": True },
								columnSize="sizeToFit",
							)
						]
					),
					# TODO: top vendors table
					dmc.GridCol(
						span=4,
						children=[
							dag.AgGrid(
								id="performance-vendors",
								style={ "height": "264px" },
								# TODO
								rowData=[{
									'place_name': "TODO Vendor " + str(i),
									'count': 0,
									'sum': 0,
									'commission': 0,
								} for i in range(5)],
								columnDefs=[
									{ 'headerName': 'Vendor', 'field': 'vendor_name' },
									{ 'headerName': 'Count', 'field': 'count', 'type': 'numericColumn' },
									{ 'headerName': 'Sum', 'field': 'sum', "valueFormatter": { "function": f"{locale_cs_d3}.format('($,.0f')(params.value)" }, 'type': 'numericColumn' },
									{ 'headerName': 'Commission', 'field': 'commission', "valueFormatter": { "function": f"{locale_cs_d3}.format('($,.0f')(params.value)" }, 'type': 'numericColumn' },
								],
								defaultColDef={ "resizable": True, "sortable": True, "filter": True },
								columnSize="sizeToFit",
							)
						]
					),
					# TODO: top products table
					dmc.GridCol(
						span=4,
						children=[
							dag.AgGrid(
								id="performance-products",
								style={ "height": "264px" },
								# TODO
								rowData=[{
									'place_name': "TODO Product " + str(i),
									'count': 0,
									'sum': 0,
									'commission': 0,
								} for i in range(5)],
								columnDefs=[
									{ 'headerName': 'Product', 'field': 'product_name' },
									{ 'headerName': 'Count', 'field': 'count', 'type': 'numericColumn' },
									{ 'headerName': 'Sum', 'field': 'sum', "valueFormatter": { "function": f"{locale_cs_d3}.format('($,.0f')(params.value)" }, 'type': 'numericColumn' },
									{ 'headerName': 'Commission', 'field': 'commission', "valueFormatter": { "function": f"{locale_cs_d3}.format('($,.0f')(params.value)" }, 'type': 'numericColumn' },
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
