from __future__ import annotations

import datetime

from dashboard_app._db_utils import QueryDefinition, QueryManager, QueryParameter, get_db_config

# Initialize the query manager
query_manager = QueryManager(get_db_config())

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
