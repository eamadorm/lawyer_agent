# BigQuery Tool

This folder contains the BigQuery helpers and tool implementations used by the `core_agent` to list datasets/tables, fetch table schemas and execute read-only SQL queries.

Location
- Code: [backend_services/core_agent/tools/bigquery](backend_services/core_agent/tools/bigquery/)
- Main modules:
  - `bq_utils.py` — low-level wrappers around `google.cloud.bigquery.Client`.
  - `tool_functions.py` — function declarations consumed by the agent (`list_bq_datasets`, `list_bq_tables`, `get_bq_table_schema`, `execute_bq_query`).
  - `schemas.py` — Pydantic request/response models.
  - `config.py` — `BQConfig` with `PROJECT_ID`.

Auth & requirements
- The code uses `google-cloud-bigquery`. Authenticate with Application Default Credentials or set `GOOGLE_APPLICATION_CREDENTIALS` to a service account JSON key.



Key behaviors
- Read-only enforcement: `execute_bq_query` rejects queries that contain DML/DDL keywords (INSERT, UPDATE, DELETE, DROP, ALTER, CREATE, MERGE, TRUNCATE).
- Errors are raised as `ValueError` in many utility functions for invalid parameters or missing datasets/tables.

API / Tool functions (programmatic usage)

# BigQuery Tool — Function reference

This file lists the BigQuery function tools and their input/output schemas. Implementations: [tool_functions.py](backend_services/core_agent/tools/bigquery/tool_functions.py). Schemas: [schemas.py](backend_services/core_agent/tools/bigquery/schemas.py).

- `list_bq_datasets(request: BigQueryListDatasetsRequest) -> BigQueryListDatasetsResponse`
  - Input: `BigQueryListDatasetsRequest` — fields: `project_id` (AllowedBQProjects)
  - Output: `BigQueryListDatasetsResponse` — fields: `project_id`, `datasets: list[str]`, `total_datasets: int`

- `list_bq_tables(request: BigQueryListTablesRequest) -> BigQueryListTablesResponse`
  - Input: `BigQueryListTablesRequest` — fields: `project_id`, `dataset_name`
  - Output: `BigQueryListTablesResponse` — fields: `project_id`, `dataset_name`, `tables: list[str]`, `total_tables: int`

- `get_bq_table_schema(request: BigQueryGetSchemaRequest) -> BigQueryTableSchema`
  - Input: `BigQueryGetSchemaRequest` — fields: `project_id`, `dataset_name`, `table_name`
  - Output: `BigQueryTableSchema` — fields: `project_id`, `dataset_name`, `table_name`, `fields: list[google.cloud.bigquery.schema.SchemaField]` (serialized via Pydantic)

- `execute_bq_query(request: BigQueryExecuteQueryRequest) -> BigQueryExecuteQueryResponse`
  - Input: `BigQueryExecuteQueryRequest` — fields: `query: str`
  - Output: `BigQueryExecuteQueryResponse` — fields: `query: str`, `results: list[dict]` (rows)

Notes:
- Input/output models are defined in the linked `schemas.py`.
- `execute_bq_query` enforces read-only queries by rejecting DML/DDL keywords.
