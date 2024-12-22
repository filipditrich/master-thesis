from __future__ import annotations

import dash as dash
import dash_mantine_components as dmc
import plotly.graph_objects as go
from dash import dcc, html
from dash_iconify import DashIconify

from dashboard_app._chart_utils import SankeyDiagram
from dashboard_app._format_utils import format_price, format_price_short, parse_date


def cashflow_section_children(app):
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
								children=DashIconify(icon="fa6-solid:money-bill-transfer", width=25)
							),
							html.Div(
								children=[
									dmc.Title(
										size="1.25rem",
										children='Cashflow and Revenue Analysis'
									),
									dmc.Text(
										"This section provides an extensive view into event's financial data and cashflow analysis.",
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
					dmc.GridCol(
						span=4,
						children=[
							dmc.Stack(
								className="h-full",
								children=[
									# revenue
									dmc.Card(
										className="flex flex-col h-full",
										p="sm",
										withBorder=True,
										children=[
											dmc.Stack(
												gap="xs",
												className="h-full [&>div]:h-full [&>div>div]:h-full",
												children=[
													dmc.Text("Total revenue", size="sm", fw=500),
													dcc.Loading(
														type="dot",
														target_components={ "cashflow-revenue-card": "children" },
														children=[
															dmc.Stack(id="cashflow-revenue-card", gap="xs", className="h-full")
														],
													),
												]
											)
										]
									),
									dmc.Card(
										className="flex flex-col h-full",
										p="sm",
										withBorder=True,
										children=[
											dmc.Stack(
												gap="xs",
												className="h-full [&>div]:h-full [&>div>div]:h-full",
												children=[
													dmc.Text("Disposable balances", size="sm", fw=500),
													dcc.Loading(
														type="dot",
														target_components={ "cashflow-balances-card": "children" },
														children=[dmc.Stack(id="cashflow-balances-card", gap="xs", className="h-full")],
													),
												]
											)

										]
									)
								]
							)
						]
					),
					# sankey diagram
					dmc.GridCol(
						span=8,
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
											dmc.Text("Cashflow Sankey Diagram", size="sm", fw=500),
											dcc.Loading(
												type="dot",
												target_components={ "cashflow-sankey-diagram": "children" },
												children=[
													html.Div(
														id="cashflow-sankey-diagram",
														children=[]
													)
												],
											),
										]
									)
								]
							)
						]
					),
					# top-ups
					dmc.GridCol(
						span=4,
						children=[
							dmc.Card(
								className="h-full",
								p="sm",
								withBorder=True,
								children=[
									dcc.Loading(
										type="dot",
										target_components={ "cashflow-top-ups-card": "children" },
										children=[dmc.Stack(id="cashflow-top-ups-card", gap="xs", className="grow")],
									),
								]
							)
						]
					),
					# organizer sales
					dmc.GridCol(
						span=4,
						children=[
							dmc.Card(
								className="h-full",
								p="sm",
								withBorder=True,
								children=[
									dcc.Loading(
										type="dot",
										target_components={ "cashflow-organizer-sales-card": "children" },
										children=[dmc.Stack(id="cashflow-organizer-sales-card", gap="xs", className="grow")],
									),
								]
							)
						]
					),
					# external vendor sales
					dmc.GridCol(
						span=4,
						children=[
							dmc.Card(
								className="h-full",
								p="sm",
								withBorder=True,
								children=[
									dcc.Loading(
										type="dot",
										target_components={ "cashflow-external-sales-card": "children" },
										children=[dmc.Stack(id="cashflow-external-sales-card", gap="xs", className="grow")],
									),
								]
							)
						]
					),
				]
			),
		],
	)


def cashflow_section_callbacks(app):
	# cashflow revenue card callbacks
	@app.register_callback(
		background=True,
		output=(dash.Output("cashflow-revenue-card", "children")),
		inputs=(
				dash.Input("filter-date-from", "value"),
				dash.Input("filter-date-to", "value"),
		),
	)
	async def update_cashflow_revenue_card(date_from, date_to):
		results = await app.query_manager.execute_queries(
			query_names=["sankey_diagram"],
			parameters={
				"date_from": parse_date(date_from),
				"date_to": parse_date(date_to)
			}
		)
		sankey_data = results['sankey_diagram'].iloc[0]
		total_revenue = sankey_data['vendor_external_commission'] + sankey_data['vendor_organizer_sales'] - sankey_data['vendor_organizer_expenses'] + sankey_data['balance_unused_unclaimed_organizer']
		balances_ratio = sankey_data['balance_unused_unclaimed_organizer'] / total_revenue * 100
		commission_ratio = sankey_data['vendor_external_commission'] / total_revenue * 100
		sales_ratio = (sankey_data['vendor_organizer_sales'] - sankey_data['vendor_organizer_expenses']) / total_revenue * 100

		return [
			dmc.Group(
				gap="xs",
				justify="space-between",
				children=[
					dmc.Text(
						format_price(total_revenue),
						size="xl",
						fw=700
					),
					dmc.ThemeIcon(
						size="lg",
						radius="xl",
						color="green",
						variant="light",
						children=DashIconify(icon="game-icons:profit", width=20)
					),
				]
			),
			dmc.Text(
				"as total net revenue from sales, unclaimed balance and possible direct sales",
				size="sm",
				className="mt-auto",
				c="dimmed"
			),
			dmc.ProgressRoot(
				[
					dmc.ProgressSection(dmc.ProgressLabel("Balances"), value=balances_ratio, color="blue"),
					dmc.ProgressSection(dmc.ProgressLabel("Commission"), value=commission_ratio, color="indigo"),
					dmc.ProgressSection(dmc.ProgressLabel("Others"), value=sales_ratio, color="gray"),
				],
				size="xl",
			)
		]

	# cashflow balances card callbacks
	@app.register_callback(
		background=True,
		output=(dash.Output("cashflow-balances-card", "children")),
		inputs=(
				dash.Input("filter-date-from", "value"),
				dash.Input("filter-date-to", "value"),
		)
	)
	async def update_cashflow_balances_card(date_from, date_to):
		results = await app.query_manager.execute_queries(
			query_names=["sankey_diagram"],
			parameters={
				"date_from": parse_date(date_from),
				"date_to": parse_date(date_to)
			}
		)
		sankey_data = results['sankey_diagram'].iloc[0]
		unused_balance = sankey_data['balance_unused']
		unclaimed_balance = sankey_data['balance_unused_unclaimed_organizer']
		unclaimed_balance_ratio = unclaimed_balance / unused_balance * 100
		refunded_balance = sankey_data['balance_unused_refunded']
		refunded_balance_ratio = refunded_balance / unused_balance * 100

		return [
			dmc.Group(
				gap="xs",
				justify="space-between",
				children=[
					dmc.Text(
						format_price(unclaimed_balance),
						size="xl",
						fw=700
					),
					dmc.ThemeIcon(
						size="lg",
						radius="xl",
						color="green",
						variant="light",
						children=DashIconify(icon="mdi:dollar", width=20)
					),
				]
			),
			dmc.Text(
				"has been left unclaimed by customers",
				size="sm",
				className="mt-auto",
				c="dimmed"
			),
			dmc.ProgressRoot(
				[
					dmc.ProgressSection(dmc.ProgressLabel("Unclaimed"), value=unclaimed_balance_ratio, color="blue"),
					dmc.ProgressSection(dmc.ProgressLabel("Refunded"), value=refunded_balance_ratio, color="gray"),
				],
				size="xl",
			),
		]

	# cashflow top-ups card callbacks
	@app.register_callback(
		background=True,
		output=(dash.Output("cashflow-top-ups-card", "children")),
		inputs=(
				dash.Input("filter-date-from", "value"),
				dash.Input("filter-date-to", "value"),
		)
	)
	async def update_cashflow_top_ups_card(date_from, date_to):
		results = await app.query_manager.execute_queries(
			query_names=["sankey_diagram"],
			parameters={
				"date_from": parse_date(date_from),
				"date_to": parse_date(date_to)
			}
		)
		sankey_data = results['sankey_diagram'].iloc[0]
		top_up_total = sankey_data['top_up_total']
		top_up_online = sankey_data['top_up_online']
		top_up_online_ratio = top_up_online / top_up_total * 100
		top_up_card = sankey_data['top_up_card']
		top_up_card_ratio = top_up_card / top_up_total * 100
		top_up_cash = sankey_data['top_up_cash']
		top_up_cash_ratio = top_up_cash / top_up_total * 100
		top_up_vip = sankey_data['top_up_vip']
		top_up_vip_ratio = top_up_vip / top_up_total * 100

		return [
			dmc.Text("Credit top-ups", size="sm", fw=500),
			dmc.Group(
				gap="xs",
				justify="space-between",
				children=[
					dmc.Text(
						format_price(top_up_total),
						size="xl",
						fw=700
					),
					dmc.ThemeIcon(
						size="lg",
						radius="xl",
						color="green",
						variant="light",
						children=DashIconify(icon="mdi:credit-card-refresh-outline", width=20)
					),
				]
			),
			dmc.Text(
				"has been topped up in total",
				size="sm",
				c="dimmed"
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
							dmc.Group(
								justify="space-between",
								children=[
									dmc.Text("Card Terminal", size="xs"),
									dmc.Text(
										format_price_short(top_up_card),
										size="xs",
										fw=600
									)
								]
							),
							dmc.Progress(value=top_up_card_ratio, color="blue"),
						]
					),
					dmc.Stack(
						gap="xs",
						className="bg-zinc-50 p-2 border border-zinc-200 rounded-sm",
						children=[
							dmc.Group(
								justify="space-between",
								children=[
									dmc.Text("Cash", size="xs"),
									dmc.Text(
										format_price_short(top_up_cash),
										size="xs",
										fw=600
									)
								]
							),
							dmc.Progress(value=top_up_cash_ratio, color="blue"),
						]
					),
					dmc.Stack(
						gap="xs",
						className="bg-zinc-50 p-2 border border-zinc-200 rounded-sm",
						children=[
							dmc.Group(
								justify="space-between",
								children=[
									dmc.Text("Online Top-up", size="xs"),
									dmc.Text(
										format_price_short(top_up_online),
										size="xs",
										fw=600
									)
								]
							),
							dmc.Progress(value=top_up_online_ratio, color="blue"),
						]
					),
					dmc.Stack(
						gap="xs",
						className="bg-zinc-50 p-2 border border-zinc-200 rounded-sm",
						children=[
							dmc.Group(
								justify="space-between",
								children=[
									dmc.Text("VIP Issued", size="xs"),
									dmc.Text(
										format_price_short(top_up_vip),
										size="xs",
										fw=600
									)
								]
							),
							dmc.Progress(value=top_up_vip_ratio, color="yellow"),
						]
					),
				]
			)
		]

	# cashflow organizer sales card callbacks
	@app.register_callback(
		background=True,
		output=(dash.Output("cashflow-organizer-sales-card", "children")),
		inputs=(
				dash.Input("filter-date-from", "value"),
				dash.Input("filter-date-to", "value"),
		)
	)
	async def update_cashflow_organizer_sales_card(date_from, date_to):
		results = await app.query_manager.execute_queries(
			query_names=["sankey_diagram"],
			parameters={
				"date_from": parse_date(date_from),
				"date_to": parse_date(date_to)
			}
		)
		sankey_data = results['sankey_diagram'].iloc[0]
		organizer_sales = sankey_data['vendor_organizer_sales']
		organizer_non_alcoholic_sales = sankey_data['vendor_organizer_sales_non_alcoholic']
		organizer_beer_sales = sankey_data['vendor_organizer_sales_beer']
		organizer_wine_sales = sankey_data['vendor_organizer_sales_wine']
		organizer_spirits_sales = sankey_data['vendor_organizer_sales_spirits']
		organizer_salty_sales = sankey_data['vendor_organizer_sales_salty']
		organizer_sweet_sales = sankey_data['vendor_organizer_sales_sweet']
		organizer_complimentary_sales = sankey_data['vendor_organizer_sales_complimentary']
		organizer_other_sales = sankey_data['vendor_organizer_sales_other']
		organizer_ticket_sales = sankey_data['vendor_organizer_sales_ticket']

		return [
			dmc.Text("Organizer sales", size="sm", fw=500),
			dmc.Group(
				gap="xs",
				justify="space-between",
				children=[
					dmc.Text(
						format_price(organizer_sales),
						size="xl",
						fw=700
					),
					dmc.ThemeIcon(
						size="lg",
						radius="xl",
						color="green",
						variant="light",
						children=DashIconify(icon="game-icons:sell-card", width=20)
					),
				]
			),
			dmc.Text(
				"sold directly by the organizer",
				size="sm",
				c="dimmed"
			),
			dmc.Divider(className="my-1"),
			dmc.SimpleGrid(
				cols=1,
				spacing="xs",
				className="grow",
				children=[
					dmc.Stack(
						gap="xs",
						className="bg-zinc-50 p-2 border border-zinc-200 rounded-sm",
						children=[
							dmc.Group(
								justify="space-between",
								children=[
									dmc.Text("Beer beverages", size="xs"),
									dmc.Text(
										format_price_short(organizer_beer_sales),
										size="xs",
										fw=600
									)
								]
							),
							dmc.Group(
								justify="space-between",
								children=[
									dmc.Text("Other alcoholic beverages", size="xs"),
									dmc.Text(
										format_price_short(organizer_wine_sales + organizer_spirits_sales),
										size="xs",
										fw=600
									)
								]
							),
							dmc.Group(
								justify="space-between",
								children=[
									dmc.Text("Others", size="xs"),
									dmc.Text(
										format_price_short(organizer_salty_sales + organizer_sweet_sales + organizer_other_sales),
										size="xs",
										fw=600
									)
								]
							),
							dmc.Group(
								justify="space-between",
								children=[
									dmc.Text("Ticket sales in-place", size="xs"),
									dmc.Text(
										format_price_short(organizer_ticket_sales),
										size="xs",
										fw=600
									)
								]
							),
						]
					),
				]
			)
		]

	# cashflow external sales card callbacks
	@app.register_callback(
		background=True,
		output=(dash.Output("cashflow-external-sales-card", "children")),
		inputs=(
				dash.Input("filter-date-from", "value"),
				dash.Input("filter-date-to", "value"),
		)
	)
	async def update_cashflow_external_sales_card(date_from, date_to):
		results = await app.query_manager.execute_queries(
			query_names=["sankey_diagram"],
			parameters={
				"date_from": parse_date(date_from),
				"date_to": parse_date(date_to)
			}
		)
		sankey_data = results['sankey_diagram'].iloc[0]
		external_sales = sankey_data['vendor_external_sales']
		external_commission = sankey_data['vendor_external_commission']
		external_payout = sankey_data['vendor_external_payout']

		return [
			dmc.Text("External vendor sales", size="sm", fw=500),
			dmc.Group(
				gap="xs",
				justify="space-between",
				children=[
					dmc.Text(
						format_price(external_sales),
						size="xl",
						fw=700
					),
					dmc.ThemeIcon(
						size="lg",
						radius="xl",
						color="green",
						variant="light",
						children=DashIconify(icon="mdi:deal", width=20)
					),
				]
			),
			dmc.Text(
				"sold by external vendors",
				size="sm",
				c="dimmed"
			),
			dmc.Divider(className="my-1"),
			dmc.SimpleGrid(
				cols=1,
				spacing="xs",
				className="grow",
				children=[
					dmc.Stack(
						gap="xs",
						className="bg-zinc-50 p-2 border border-zinc-200 rounded-sm",
						children=[
							dmc.Group(
								justify="space-between",
								children=[
									dmc.Text("Total commission from sales", size="xs"),
									dmc.Text(
										format_price_short(external_commission),
										size="xs",
										fw=600
									)
								]
							),
							dmc.Group(
								justify="space-between",
								children=[
									dmc.Text("Vendor's payout", size="xs"),
									dmc.Text(
										format_price_short(external_payout),
										size="xs",
										fw=600
									)
								]
							),
						]
					),
				]
			)
		]

	# cashflow sankey diagram callbacks
	@app.register_callback(
		background=True,
		output=(dash.Output("cashflow-sankey-diagram", "children")),
		inputs=(
				dash.Input("filter-date-from", "value"),
				dash.Input("filter-date-to", "value"),
		),
	)
	async def update_cashflow_sankey_diagram(date_from, date_to):
		results = await app.query_manager.execute_queries(
			query_names=["sankey_diagram"],
			parameters={
				"date_from": parse_date(date_from),
				"date_to": parse_date(date_to)
			}
		)
		sankey_data = results['sankey_diagram']

		diagram = SankeyDiagram()

		# top-ups
		diagram.add_node('top_up_online', 'Online top-up', x=0.05, y=-0.2, color='indigo')
		diagram.add_node('top_up_card', 'Card top-up', x=0.05, y=0.2, color='cool_gray')
		diagram.add_node('top_up_cash', 'Cash top-up', x=0.05, y=0.4, color='cool_gray')
		diagram.add_node('top_up_vip', 'VIP top-up', x=0.05, y=0.6, color='warm_gray')

		# chip balances
		diagram.add_node('chip_balances', 'Chip balances', x=0.2, y=0.4, color='slate_blue')
		diagram.add_flow('top_up_online', 'chip_balances', sankey_data['top_up_online'] / 100, color=None)
		diagram.add_flow('top_up_card', 'chip_balances', sankey_data['top_up_card'] / 100, color=None)
		diagram.add_flow('top_up_cash', 'chip_balances', sankey_data['top_up_cash'] / 100, color=None)
		diagram.add_flow('top_up_vip', 'chip_balances', sankey_data['top_up_vip'] / 100, color=None)

		# non-chip sales
		diagram.add_node('non_chip_card', 'Card payments', x=0.2, y=0.6, color='light_steel')
		diagram.add_node('non_chip_cash', 'Cash payments', x=0.2, y=0.65, color='light_steel')

		# event finances
		diagram.add_node('event_finances', 'Event finances', x=0.4, y=0.5, color='warm_gray')
		diagram.add_flow('chip_balances', 'event_finances', sankey_data['top_up_total'] / 100, color=None)
		diagram.add_flow('non_chip_card', 'event_finances', sankey_data['non_chip_card'] / 100, color=None)
		diagram.add_flow('non_chip_cash', 'event_finances', sankey_data['non_chip_cash'] / 100, color=None)

		# vendor sales
		diagram.add_node('vendor_sales', 'Vendor sales', x=0.6, y=0.3, color='dusty_blue')
		diagram.add_flow('event_finances', 'vendor_sales', sankey_data['vendor_sales'] / 100, color=None)

		# external vendor sales
		diagram.add_node('vendor_external_sales', 'External vendor sales', x=0.65, y=0.3, color='dusty_blue')
		diagram.add_flow('vendor_sales', 'vendor_external_sales', sankey_data['vendor_external_sales'] / 100, color=None)
		# external vendor payouts
		diagram.add_node('vendor_external_payout', 'Vendor external payout', x=0.8, y=0.2, color='mint')
		diagram.add_flow('vendor_external_sales', 'vendor_external_payout', sankey_data['vendor_external_payout'] / 100, color=None)

		# organizer vendor sales + expenses
		diagram.add_node('vendor_organizer_sales', 'Organizer direct sales', x=0.65, y=0.3, color='dusty_blue')
		diagram.add_flow('vendor_sales', 'vendor_organizer_sales', sankey_data['vendor_organizer_sales'] / 100, color=None)
		diagram.add_node('vendor_organizer_expenses', 'Organizer sale expenses', x=0.65, y=0.3, color='dusty_blue')
		diagram.add_flow('vendor_organizer_sales', 'vendor_organizer_expenses', sankey_data['vendor_organizer_expenses'] / 100, color=None)

		# unused credit
		diagram.add_node('balance_unused', 'Unused credit', x=0.6, y=0.8, color='peach')
		diagram.add_flow('event_finances', 'balance_unused', sankey_data['balance_unused'] / 100, color=None)

		# unclaimed credit
		diagram.add_node('balance_unused_unclaimed', 'Unclaimed credit', x=0.6, y=0.8, color='peach')
		diagram.add_flow('balance_unused', 'balance_unused_unclaimed', sankey_data['balance_unused_unclaimed'] / 100, color=None)

		# refunded credit
		diagram.add_node('balance_unused_refunded', 'Refunded credit', x=0.6, y=0.8, color='peach')
		diagram.add_flow('balance_unused', 'balance_unused_refunded', sankey_data['balance_unused_refunded'] / 100, color=None)

		# organizer revenue
		diagram.add_node('organizer_revenue', 'Organizer revenue', x=0.99, y=0.7, color='lavender')
		diagram.add_flow('vendor_external_sales', 'organizer_revenue', sankey_data['vendor_external_commission'] / 100, color=None)
		diagram.add_flow('vendor_organizer_sales', 'organizer_revenue', (sankey_data['vendor_organizer_sales'] - sankey_data['vendor_organizer_expenses']) / 100, color=None)
		diagram.add_flow('balance_unused_unclaimed', 'organizer_revenue', sankey_data['balance_unused_unclaimed_organizer'] / 100, color=None)

		# Create the figure
		fig = go.Figure(
			data=[go.Sankey(
				arrangement='snap',
				**diagram.to_plotly()
			)]
		)

		# Update layout
		fig.update_layout(
			font_size=12,
			height=325,
			width=800,
			margin=dict(l=25, r=25, t=25, b=25),
			plot_bgcolor='rgba(0,0,0,0)',
			paper_bgcolor='rgba(0,0,0,0)'
		)

		return [
			dcc.Graph(
				id="sankey-chart",
				figure=fig,
				config={
					# "displayModeBar": False,
				}
			)
		]
