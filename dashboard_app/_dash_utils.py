from __future__ import annotations

import os
from uuid import uuid4

import diskcache
import dash

# use optimized directory for cache usage
CACHE_DIR = os.path.join(os.path.dirname(__file__), 'dash_cache')
os.makedirs(CACHE_DIR, exist_ok=True)
# cache configuration
cache = diskcache.Cache(
	directory=CACHE_DIR,
	size_limit=3e9,
	eviction_policy='least-recently-used',
)

# unique launch_uid to refresh cache when the app restarts
launch_uid = uuid4()
background_callback_manager = dash.DiskcacheManager(
	cache,
	cache_by=[
		lambda: launch_uid,
	],
	expire=300
)


def create_cache_key(callback_id: str):
	"""Create a cache key for a callback with an ID"""
	scoped_cache_dir = os.path.join(CACHE_DIR, callback_id)
	os.makedirs(scoped_cache_dir, exist_ok=True)
	return dash.DiskcacheManager(
		cache=diskcache.Cache(
			directory=scoped_cache_dir,
			size_limit=3e9,
			eviction_policy='least-recently-used',
		),
		cache_by=[
			lambda: launch_uid,
			lambda: callback_id,
		],
		expire=300
	)


external_script = ["https://tailwindcss.com/", { "src": "https://cdn.tailwindcss.com" }]
index_string = """<!DOCTYPE html>
<html>
    <head>
        {%metas%}
        <title>{%title%}</title>
        {%favicon%}
        {%css%}
        <style>
            #react-entry-point, #_dash-app-content {
                display: flex;
                flex-direction: column;
                flex-grow: 1;
                min-height: 100vh;
            }
        </style>
    </head>
    <body class="min-h-screen flex flex-col bg-zinc-50">
        {%app_entry%}
        <footer>
            {%config%}
            {%scripts%}
            {%renderer%}
        </footer>
    </body>
</html>
"""
