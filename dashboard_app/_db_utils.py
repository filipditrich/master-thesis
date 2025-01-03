from __future__ import annotations, annotations

import asyncio
import hashlib
import os
import re
from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Any, Callable, Dict, List, Optional

import asyncpg
import pandas as pd

LOG_CACHE = False


def get_db_config():
	return {
		"database": "postgres",
		"user": "postgres",
		"password": "",
		"host": "localhost",
		"port": "5431",
		# "sslmode": "disable"
	}


# ---- Data Models ----
@dataclass
class QueryParameter:
	name: str
	type: type
	required: bool = True
	default: Any = None
	validator: Optional[Callable[[Any], bool]] = None


@dataclass
class QueryDefinition:
	name: str
	sql: str
	parameters: List[QueryParameter]
	description: str = ""
	default_data: Optional[pd.DataFrame] | str = None

	def __init__(self, name: str, sql: str, parameters: List[QueryParameter], description: str = "", default_data: Optional[pd.DataFrame] | str = None):
		self.name = name
		self.sql = sql
		self.parameters = parameters
		self.description = description
		self.default_data = default_data


class DataTransformer(ABC):
	@abstractmethod
	async def transform(self, df: pd.DataFrame) -> pd.DataFrame:
		pass


class SimpleTransformer(DataTransformer):
	def __init__(self, transform_fn: Callable[[pd.DataFrame], pd.DataFrame]):
		self.transform_fn = transform_fn

	async def transform(self, df: pd.DataFrame) -> pd.DataFrame:
		return self.transform_fn(df)


# ---- Query Registry ----
class QueryRegistry:
	def __init__(self):
		self._queries: Dict[str, QueryDefinition] = { }
		self._transformers: Dict[str, List[DataTransformer]] = { }

	def register_query(self, query_def: QueryDefinition):
		self._queries[query_def.name] = query_def
		return self

	def register_transformer(self, query_name: str, transformer: DataTransformer):
		if query_name not in self._transformers:
			self._transformers[query_name] = []
		self._transformers[query_name].append(transformer)
		return self

	def get_query(self, name: str) -> QueryDefinition:
		return self._queries[name]

	def get_transformers(self, name: str) -> List[DataTransformer]:
		return self._transformers.get(name, [])


class QueryManager:
	def __init__(self, db_config: Dict[str, str]):
		self.db_config = db_config
		self.pool = None
		self.registry = QueryRegistry()
		self._initialize_queries()
		self._pool_lock = asyncio.Lock()

	def _initialize_queries(self):
		"""Register all queries and transformers"""
		pass

	@staticmethod
	def process_sql_query(sql_query: str) -> str:
		"""Process an SQL query to replace dynamic named parameters with positional parameters"""
		# replace all dynamic named parameters ":param_name$n" with "n" using regex
		output_query = sql_query
		params = re.findall(r"\:\w+\$\d+", output_query)
		for param in params:
			# get the number from the dynamic named parameter
			num = param.split("$")[-1]
			# replace the dynamic named parameter with the number
			output_query = output_query.replace(param, f"${num}")

		return output_query

	@staticmethod
	def read_sql_query(filename: str) -> str:
		"""Read a SQL query from queries/ directory repo"""
		file_path = os.path.join(os.getcwd(), "dashboard_app", "queries", filename)
		with open(file_path, "r") as f:
			sql_file = f.read()
			return QueryManager.process_sql_query(sql_file)

	async def init_pool(self):
		async with self._pool_lock:
			if not self.pool:
				try:
					self.pool = await asyncpg.create_pool(
						**self.db_config,
						min_size=5,
						max_size=20,
						command_timeout=60,
						max_queries=50000,
						# Add connection timeout
						timeout=10.0,
						# Add connection retry logic
						# setup=lambda conn: conn.add_listener(
						# 	'connection_cleanup',
						# 	lambda conn: asyncio.create_task(self._cleanup_connection(conn))
						# )
					)
				except Exception as e:
					print(f"Failed to create connection pool: {e}")
					raise

	async def _cleanup_connection(self, conn):
		"""Cleanup callback for terminated connections"""
		try:
			if not conn.is_closed():
				await conn.close()
		except Exception as e:
			print(f"Error during connection cleanup: {e}")

	async def close_pool(self):
		"""Properly close the connection pool"""
		if self.pool:
			async with self._pool_lock:
				await self.pool.close()
				self.pool = None

	def get_query_key(self, query_name: str, parameters: Dict[str, Any]) -> str:
		"""
		Generate a unique key for a query based on its name and parameters.
		The key should be hashed but fixed for the same query and parameters to allow caching even across restarts.
		"""
		# Sort parameters by name to ensure consistent order
		sorted_params = sorted(parameters.items())
		# Convert parameters to a string
		param_str = ",".join(f"{k}={v}" for k, v in sorted_params)
		# Use hashlib for a consistent hash across sessions
		param_str_hash = hashlib.md5(param_str.encode()).hexdigest()
		# Combine query name and parameters
		return f"{param_str_hash}/{query_name}"

	async def execute_query(self, query_name: str, parameters: Dict[str, Any], or_query_def: Optional[QueryDefinition]) -> pd.DataFrame:
		"""Execute a single query by name with given parameters"""
		query_def = or_query_def if or_query_def else self.registry.get_query(query_name)
		query_key = self.get_query_key(query_name, parameters)

		# Return default data if available
		if query_def.default_data is not None:
			if query_def.default_data == "FSCacheDefault":
				try:
					if LOG_CACHE:
						print(f"⚡ Returning cached data for query {query_name}")
					# read CSV from cache
					file_path = os.path.join(os.getcwd(), "dashboard_app", "cached-queries", f"{query_key}.csv")
					csv = pd.read_csv(file_path)
					# replace NaN with None
					csv = csv.where(pd.notnull(csv), None)
					# return the cached data as a DataFrame
					return csv
				except Exception as e:
					pass
			else:
				if LOG_CACHE:
					print(f"Returning default data for query {query_name}")
				return query_def.default_data

		# Initialize pool if needed
		await self.init_pool()

		max_retries = 3
		retry_delay = 1.0  # seconds

		for attempt in range(max_retries):
			try:
				async with self.pool.acquire() as conn:
					print(f"⌛ Executing query {query_name}")
					# Execute the query and get both records and description
					stmt = await conn.prepare(query_def.sql)
					records = await stmt.fetch(
						*[
							parameters.get(param.name, param.default)
							for param in query_def.parameters
						]
					)

					# Get column names from the statement
					column_names = [desc.name for desc in stmt.get_attributes()]

					# Create DataFrame with explicit column names
					df = pd.DataFrame(records, columns=column_names)

					# Apply transformers
					for transformer in self.registry.get_transformers(query_name):
						df = await transformer.transform(df)

					# Save the result to local file cache
					if LOG_CACHE:
						print(f"💾 Saving query {query_name} to cache as {query_key}")
					try:
						# get the directories from query_key
						dir_path = "/".join(query_key.split("/")[:-1])
						# create the directories if they don't exist
						os.makedirs(os.path.join(os.getcwd(), "dashboard_app", "cached-queries", dir_path), exist_ok=True)
						# save the query result to a csv file
						df.to_csv(os.path.join(os.getcwd(), "dashboard_app", "cached-queries", f"{query_key}.csv"), index=False)
					except Exception as e:
						print(f"Failed to save query {query_name} to cache: {e}")

					return df

			except (asyncpg.ConnectionDoesNotExistError, asyncpg.ConnectionFailureError) as e:
				if attempt == max_retries - 1:
					print(f"Failed to execute query after {max_retries} attempts: {e}")
					raise
				print(f"Connection error on attempt {attempt + 1}, retrying in {retry_delay} seconds...")
				await asyncio.sleep(retry_delay)
				# Reset the pool on connection errors
				await self.close_pool()
				await self.init_pool()

			except Exception as e:
				print(f"🚨 Error executing query {query_name}: {e}")
				raise

	async def execute_queries(self, query_names: List[str], parameters: Dict[str, Any], or_query_defs: Dict[str, QueryDefinition] = { }) -> Dict[str, pd.DataFrame]:
		"""Execute multiple queries concurrently"""
		await self.init_pool()

		async def execute_single_query(name: str) -> tuple[str, pd.DataFrame]:
			df = await self.execute_query(name, parameters, or_query_defs.get(name))
			return name, df

		# Execute specified queries concurrently
		tasks = [execute_single_query(name) for name in query_names]
		try:
			results = await asyncio.gather(*tasks)
			return dict(results)
		except Exception as e:
			print(f"Error executing queries: {e}")
			# Ensure pool is closed on error
			await self.close_pool()
			raise
