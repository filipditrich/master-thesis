from __future__ import annotations

import asyncio

import dash as dash
import dash_mantine_components as dmc
import pandas as pd
from dash import html

from dashboard_app._dash_utils import background_callback_manager, create_cache_key, external_script, index_string
from dashboard_app._query_manager import query_manager
from dashboard_app.sections.app_beverages_section import beverages_section_callbacks, beverages_section_children
from dashboard_app.sections.app_cashflow_section import cashflow_section_callbacks, cashflow_section_children
from dashboard_app.sections.app_customers_section import customers_section_callbacks, customers_section_children
from dashboard_app.sections.app_performance_section import performance_section_callbacks, performance_section_children

# set the React version
dash.dash._dash_renderer._set_react_version("18.2.0")

# (day starts at 06:00am, day ends 05:59am +1 next day)
days = {
	'1': ('2024-07-04 06:00:00', '2024-07-05 05:59:59'),
	'2': ('2024-07-05 06:00:00', '2024-07-06 05:59:59'),
	'3': ('2024-07-06 06:00:00', '2024-07-07 05:59:59'),
	'up-to-1': ('2024-07-04 06:00:00', '2024-07-05 05:59:59'),
	'up-to-2': ('2024-07-04 06:00:00', '2024-07-06 05:59:59'),
	'up-to-3': ('2024-07-04 06:00:00', '2024-07-07 05:59:59'),
}


def fast_preview_playground():
	return []


# ---- Dash Application ----
class MainApplication:
	def __init__(self):
		self._callbacks_registered = False

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

	def register_callback(self, output, inputs, prevent_initial_call=False, background=False, *args, **kwargs):
		"""
		Decorator for Dash callbacks that handles async operations and error handling.

		Args:
				output: Dash Output or tuple of Outputs
				inputs: Dash Input or tuple of Inputs
				prevent_initial_call: Boolean to prevent initial callback
				background: Boolean to run callback in background
		"""

		def decorator(func):
			# print(f"Registering callback for function {func.__name__}, Output: {output}")

			def async_callback_wrapper(_self, *args, **kwargs):
				"""Async callback wrapper implementation"""

				async def async_function():
					try:
						# TODO: parse args logic?
						parsed_args = args

						# Call the original function with parsed arguments
						return await func(_self, *parsed_args, **kwargs)
					except Exception as e:
						print(f"🚨 Error in callback {func.__name__}: {str(e)}")
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
					print(f"🚨 Error in callback {func.__name__}: {str(e)}")
					raise dash.exceptions.PreventUpdate

			# Register the callback with Dash
			if background:
				return self.__app.callback(
					output=output,
					inputs=inputs,
					background=True,
					prevent_initial_call=prevent_initial_call,
					manager=create_cache_key(func.__name__),
					*args, **kwargs
				)(async_callback_wrapper)
			else:
				return self.__app.callback(
					output=output,
					inputs=inputs,
					prevent_initial_call=prevent_initial_call,
					*args, **kwargs
				)(sync_callback_wrapper)

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
							# TODO: Filter bar
							html.Div(
								className="flex items-center justify-center gap-4",
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
											{ "value": "up-to-1", "label": "Up to Day 1" },
											{ "value": "up-to-2", "label": "Up to Day 2" },
											{ "value": "up-to-3", "label": "Up to Day 3" },
											{ "value": "all", "label": "Whole festival" },
										],
										w=200,
									),
								]
							),
							# FIXME
							fast_preview_playground(),
							# Main content
							html.Main(
								className="grid grid-cols-1 gap-4",
								children=[
									# TODO: Cashflow and Revenue Analysis
									cashflow_section_children(self),
									# TODO: Performance Analysis
									performance_section_children(self),
									# TODO: Beverage Consumption analysis
									beverages_section_children(self),
									# TODO: Customer Analysis
									customers_section_children(self),
								]
							),
							# TODO: Footer
							html.Footer(
								children=[]
							)
						]
					),
				],
			)
		)

	def _register_callbacks(self):
		if self._callbacks_registered:
			print("Callbacks already registered!")
			return

		# sync date preset with date inputs
		@self.register_callback(
			output=(dash.Output("filter-date-from", "value"), dash.Output("filter-date-to", "value")),
			inputs=(dash.Input("filter-date-preset", "value")),
		)
		def sync_date_preset(preset):
			return days[preset] if preset in days else (days['1'][0], days['3'][1])

		# FIXME: register cashflow section callbacks
		cashflow_section_callbacks(self)

		# FIXME: register performance section callbacks
		performance_section_callbacks(self)

		# FIXME: register beverages section callbacks
		beverages_section_callbacks(self)

		# FIXME: register customers section callbacks
		customers_section_callbacks(self)

		self._callbacks_registered = True

	@property
	def app(self):
		return self.__app


# run the app
if __name__ == '__main__':
	print("\n\n\n\n\n\n\n\n\n\n")
	print(f"-- Starting the dashboard app --")
	print(f"-- Started at: {pd.Timestamp.now()} --")
	print("----------------------------------------------")
	Application = MainApplication()
	app = Application.app
	app.run(debug=True, port=4001)
# app.run_server(debug=False, host='192.168.0.167', port=4000)
