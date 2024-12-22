from __future__ import annotations

import datetime

import dash_mantine_components as dmc
import dateutil
import networkx as nx
import numpy as np
import pandas as pd
import plotly.graph_objects as go
from dash import dash, dcc, html
from dash_iconify import DashIconify

from dashboard_app._db_utils import QueryDefinition, QueryManager, QueryParameter

from dashboard_app._format_utils import parse_date


def create_heatmap(df, top_n=15):
	# Get top N items by total count
	top_items = pd.concat([df['product1'], df['product2']]).value_counts().nlargest(top_n).index

	# Filter dataframe for top items
	mask = df['product1'].isin(top_items) & df['product2'].isin(top_items)
	df_filtered = df[mask]

	# Create pivot table
	pivot_table = pd.pivot_table(
		df_filtered,
		values='count',
		index='product1',
		columns='product2',
		fill_value=0
	)

	# Create heatmap
	fig = go.Figure(
		data=go.Heatmap(
			z=pivot_table.values,
			x=pivot_table.columns,
			y=pivot_table.index,
			colorscale='Blues'
		)
	)

	fig.update_layout(
		title='Top Product Combinations',
		height=600,
		xaxis_title='Product 2',
		yaxis_title='Product 1',
		margin=dict(t=30, l=5, r=5, b=5)
	)

	# Rotate x-axis labels for better readability
	fig.update_xaxes(tickangle=45)

	return fig


def create_network(df, min_count=100):
	# Filter for significant connections
	df_filtered = df[df['count'] >= min_count]

	# Create network graph
	graph = nx.Graph()

	# Add edges with weights
	for _, row in df_filtered.iterrows():
		graph.add_edge(row['product1'], row['product2'], weight=row['count'])

	# Get node positions using a layout algorithm
	pos = nx.spring_layout(graph, k=1 / np.sqrt(len(graph.nodes())), iterations=50)

	# Create edge trace
	edge_x = []
	edge_y = []

	for edge in graph.edges():
		x0, y0 = pos[edge[0]]
		x1, y1 = pos[edge[1]]
		edge_x.extend([x0, x1, None])
		edge_y.extend([y0, y1, None])

	edges_trace = go.Scatter(
		x=edge_x, y=edge_y,
		line=dict(width=1, color='#888'),
		hoverinfo='none',
		mode='lines'
	)

	# Create nodes trace
	node_x = []
	node_y = []
	node_text = []

	for node in graph.nodes():
		x, y = pos[node]
		node_x.append(x)
		node_y.append(y)
		node_text.append(node)

	nodes_trace = go.Scatter(
		x=node_x, y=node_y,
		mode='markers+text',
		hoverinfo='text',
		text=node_text,
		textposition="top center",
		marker=dict(
			size=20,
			color='#1f77b4',
			line_width=2
		)
	)

	# Create figure
	fig = go.Figure(
		data=[edges_trace, nodes_trace],
		layout=go.Layout(
			title='Product Combinations Network',
			showlegend=False,
			hovermode='closest',
			height=600,
			margin=dict(t=30, l=5, r=5, b=5),
			xaxis=dict(showgrid=False, zeroline=False, showticklabels=False),
			yaxis=dict(showgrid=False, zeroline=False, showticklabels=False)
		)
	)

	return fig


def customers_section_children(app):
	return html.Section(
		className="flex flex-col bg-white rounded-lg border border-zinc-200",
		children=[
			# Header
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
										"Insights into customer purchasing patterns and product combinations.",
										c="dimmed",
									),
								]
							)
						],
					),
				]
			),
			# Content
			dmc.Grid(
				gutter="md",
				p="md",
				grow=True,
				children=[
					# Controls
					dmc.GridCol(
						span=12,
						children=dmc.Group(
							# position="left",
							gap="md",
							children=[
								dmc.NumberInput(
									id="min-count-slider",
									label="Minimum Combination Count",
									value=100,
									min=10,
									max=1000,
									step=10,
									style={ "width": 200 }
								),
								dmc.NumberInput(
									id="top-n-products",
									label="Top N Products",
									value=15,
									min=5,
									max=30,
									step=5,
									style={ "width": 200 }
								),
							]
						)
					),
					# Heatmap
					dmc.GridCol(
						span=6,
						children=dmc.Card(
							children=dcc.Graph(id="product-heatmap"),
							withBorder=True,
							className="bg-zinc-50"
						)
					),
					# Network Graph
					dmc.GridCol(
						span=6,
						children=dmc.Card(
							children=dcc.Graph(id="product-network"),
							withBorder=True,
							className="bg-zinc-50"
						)
					)
				]
			)
		],
	)


def customers_section_callbacks(app):
	@app.register_callback(
		background=True,
		output=(
				dash.Output("product-heatmap", "figure"),
				dash.Output("product-network", "figure")
		),
		inputs=(
				dash.Input("min-count-slider", "value"),
				dash.Input("top-n-products", "value"),
				dash.Input("filter-date-from", "value"),
				dash.Input("filter-date-to", "value"),
		)
	)
	async def update_graphs(min_count, top_n, date_from, date_to):
		# Load and process the data
		# Note: You'll need to modify this part based on how your data is stored/accessed
		results = await app.query_manager.execute_queries(
			query_names=["product_network"],
			or_query_defs={
				'product_network': QueryDefinition(
					name="product_network",
					sql=QueryManager.process_sql_query(
						"""
						SELECT
							tp1.name AS product1,
							tp2.name AS product2,
							COUNT(*) AS count
						FROM pos_order_products_rich tp1
							INNER JOIN pos_order_products_rich tp2 ON tp2.transaction_id = tp1.transaction_id
						WHERE tp1.product_id < tp2.product_id
							AND tp1.created BETWEEN :date_from$1 AND :date_to$2
							AND tp2.created BETWEEN :date_from$1 AND :date_to$2
						GROUP BY tp1.name, tp2.name
						ORDER BY count DESC;
						"""
					),
					parameters=[
						QueryParameter("date_from", datetime.datetime),
						QueryParameter("date_to", datetime.datetime)
					],
					default_data="FSCacheDefault"
				)
			},
			parameters={
				"date_from": parse_date(date_from),
				"date_to": parse_date(date_to)
			}
		)
		product_network = results['product_network']

		# Create the visualizations
		heatmap_fig = create_heatmap(product_network, top_n=top_n)
		network_fig = create_network(product_network, min_count=min_count)

		return heatmap_fig, network_fig
