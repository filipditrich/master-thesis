from __future__ import annotations

import datetime

from db_utils import QueryDefinition, QueryManager, QueryParameter, get_db_config

# Initialize the query manager
query_manager = QueryManager(get_db_config())

# orders_stats query
query_manager.registry.register_query(
	QueryDefinition(
		name="orders_stats",
		sql=QueryManager.read_sql_query("orders_stats.sql"),
		parameters=[
			QueryParameter("date_from", datetime.datetime),
			QueryParameter("date_to", datetime.datetime)
		],
		default_data="FSCacheDefault"
	)
)

# order_sales_stats query
query_manager.registry.register_query(
	QueryDefinition(
		name="order_sales_stats",
		sql=QueryManager.read_sql_query("order_sales_stats.sql"),
		parameters=[
			QueryParameter("date_from", datetime.datetime),
			QueryParameter("date_to", datetime.datetime)
		],
		default_data="FSCacheDefault"
	)
)

# vip_order_sales_stats query
query_manager.registry.register_query(
	QueryDefinition(
		name="vip_order_sales_stats",
		sql=QueryManager.read_sql_query("vip_order_sales_stats.sql"),
		parameters=[
			QueryParameter("date_from", datetime.datetime),
			QueryParameter("date_to", datetime.datetime)
		],
		default_data="FSCacheDefault"
	)
)

# order_refunds_stats query
query_manager.registry.register_query(
	QueryDefinition(
		name="order_refunds_stats",
		sql=QueryManager.read_sql_query("order_refunds_stats.sql"),
		parameters=[
			QueryParameter("date_from", datetime.datetime),
			QueryParameter("date_to", datetime.datetime)
		],
		default_data="FSCacheDefault"
	)
)

# cups_stats query
query_manager.registry.register_query(
	QueryDefinition(
		name="cups_stats",
		sql=QueryManager.read_sql_query("cups_stats.sql"),
		parameters=[
			QueryParameter("date_from", datetime.datetime),
			QueryParameter("date_to", datetime.datetime)
		],
		default_data="FSCacheDefault"
	)
)

# sales_time_series query
query_manager.registry.register_query(
	QueryDefinition(
		name="sales_time_series",
		sql=QueryManager.read_sql_query("sales_time_series.sql"),
		parameters=[
			QueryParameter("date_from", datetime.datetime),
			QueryParameter("date_to", datetime.datetime)
		],
		default_data="FSCacheDefault",
	)
)
# product_category_stats query
query_manager.registry.register_query(
	QueryDefinition(
		name="product_category_stats",
		sql=QueryManager.read_sql_query("product_category_stats.sql"),
		parameters=[
			QueryParameter("date_from", datetime.datetime),
			QueryParameter("date_to", datetime.datetime)
		],
		default_data="FSCacheDefault"
	)
)

# Total Sales Overview
query_manager.registry.register_query(
	QueryDefinition(
		name="total_sales_overview",
		sql=QueryManager.read_sql_query("total_sales_overview.sql"),
		parameters=[
			QueryParameter("date_from", datetime.datetime),
			QueryParameter("date_to", datetime.datetime)
		],
		default_data="FSCacheDefault"
	)
)

# Organizer Revenue
query_manager.registry.register_query(
	QueryDefinition(
		name="organizer_revenue",
		sql=QueryManager.read_sql_query("organizer_revenue.sql"),
		parameters=[
			QueryParameter("date_from", datetime.datetime),
			QueryParameter("date_to", datetime.datetime)
		],
		default_data="FSCacheDefault"
	)
)

# Transaction Volume
query_manager.registry.register_query(
	QueryDefinition(
		name="transaction_volume",
		sql=QueryManager.read_sql_query("transaction_volume.sql"),
		parameters=[
			QueryParameter("date_from", datetime.datetime),
			QueryParameter("date_to", datetime.datetime)
		],
		default_data="FSCacheDefault"
	)
)

# Customer Base
# FIXME: remove, replaced by other queries
query_manager.registry.register_query(
	QueryDefinition(
		name="customer_base",
		sql=QueryManager.read_sql_query("customer_base.sql"),
		parameters=[
			QueryParameter("date_from", datetime.datetime),
			QueryParameter("date_to", datetime.datetime)
		],
		default_data="FSCacheDefault"
	)
)

# Chip refunds
query_manager.registry.register_query(
	QueryDefinition(
		name="chip_refunds",
		sql=QueryManager.read_sql_query("chip_refunds.sql"),
		parameters=[
			QueryParameter("date_from", datetime.datetime),
			QueryParameter("date_to", datetime.datetime)
		],
		default_data="FSCacheDefault"
	)
)

# Time series query
query_manager.registry.register_query(
	QueryDefinition(
		name="time_series",
		sql=QueryManager.read_sql_query("time_series.sql"),
		parameters=[
			QueryParameter("date_from", datetime.datetime),
			QueryParameter("date_to", datetime.datetime)
		],
		default_data="FSCacheDefault"
	)
)

# Event entry timeline query
query_manager.registry.register_query(
	QueryDefinition(
		name="event_entry_timeline",
		sql=QueryManager.read_sql_query("event_entry_timeline.sql"),
		parameters=[
			QueryParameter("date_from", datetime.datetime),
			QueryParameter("date_to", datetime.datetime)
		],
		default_data="FSCacheDefault"
	)
)

# Sankey diagram query
query_manager.registry.register_query(
	QueryDefinition(
		name="sankey_diagram",
		sql=QueryManager.read_sql_query("sankey_diagram.sql"),
		parameters=[
			QueryParameter("date_from", datetime.datetime),
			QueryParameter("date_to", datetime.datetime)
		],
		default_data="FSCacheDefault"
	)
)

# Customers - order stats grouped
query_manager.registry.register_query(
	QueryDefinition(
		name="customer_order_stats_grouped",
		sql=QueryManager.read_sql_query("customer_order_stats_grouped.sql"),
		parameters=[
			QueryParameter("date_from", datetime.datetime),
			QueryParameter("date_to", datetime.datetime),
			QueryParameter("grouping_key", str)
		],
		default_data="FSCacheDefault"
	)
)

# Customers - top up stats grouped
query_manager.registry.register_query(
	QueryDefinition(
		name="customer_topup_stats_grouped",
		sql=QueryManager.read_sql_query("customer_topup_stats_grouped.sql"),
		parameters=[
			QueryParameter("date_from", datetime.datetime),
			QueryParameter("date_to", datetime.datetime),
			QueryParameter("grouping_key", str)
		],
		default_data="FSCacheDefault"
	)
)

# Customers - activity stats grouped
query_manager.registry.register_query(
	QueryDefinition(
		name="customer_activity_stats_grouped",
		sql=QueryManager.read_sql_query("customer_activity_stats_grouped.sql"),
		parameters=[
			QueryParameter("date_from", datetime.datetime),
			QueryParameter("date_to", datetime.datetime),
			QueryParameter("grouping_key", str)
		],
		default_data="FSCacheDefault"
	)
)

# Customers - refunds stats grouped
query_manager.registry.register_query(
	QueryDefinition(
		name="customer_refund_stats_grouped",
		sql=QueryManager.read_sql_query("customer_refund_stats_grouped.sql"),
		parameters=[
			QueryParameter("date_from", datetime.datetime),
			QueryParameter("date_to", datetime.datetime),
			QueryParameter("grouping_key", str)
		],
		default_data="FSCacheDefault"
	)
)
