from __future__ import annotations

import datetime

import pandas as pd

from dashboard_app._db_utils import QueryDefinition, QueryManager, QueryParameter, get_db_config

# Initialize the query manager
query_manager = QueryManager(get_db_config())

# Sankey diagram query
query_manager.registry.register_query(
	QueryDefinition(
		name="sankey_diagram",
		sql=QueryManager.process_sql_query(
			"""
			SELECT * FROM get_sankey_diagram_data(:date_from$1, :date_to$2)
			"""
		),
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
		sql=QueryManager.process_sql_query(
			"""
			SELECT * FROM get_time_series(:date_from$1, :date_to$2, :granularity_minutes$3, :day_start_hour$4)
			"""
		),
		parameters=[
			QueryParameter("date_from", datetime.datetime),
			QueryParameter("date_to", datetime.datetime),
			QueryParameter("granularity_minutes", int),
			QueryParameter("day_start_hour", int)
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
