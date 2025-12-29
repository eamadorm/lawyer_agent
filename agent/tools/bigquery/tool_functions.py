from loguru import logger
import re
from .bq_utils import (
    query_data,
    list_datasets,
    list_dataset_tables,
    get_table_schema,
)
from .schemas import (
    BigQueryTableSchema,
    BigQueryListDatasetsRequest,
    BigQueryListDatasetsResponse,
    BigQueryListTablesRequest,
    BigQueryListTablesResponse,
    BigQueryGetSchemaRequest,
    BigQueryExecuteQueryRequest,
    BigQueryExecuteQueryResponse,
)


def list_bq_datasets(
    request: BigQueryListDatasetsRequest,
) -> BigQueryListDatasetsResponse:
    """
    List all datasets in a BigQuery project.

    Args:
        request (BigQueryListDatasetsRequest): The request object containing the project_id.

    Returns:
        BigQueryListDatasetsResponse: A list of dataset IDs.
    """
    logger.info("Listing datasets...")
    project_id = request.project_id

    datasets = list_datasets(project_id)
    logger.info(f"Found {len(datasets)} datasets")
    return BigQueryListDatasetsResponse(
        project_id=project_id,
        datasets=datasets,
        total_datasets=len(datasets),
    )


def list_bq_tables(
    request: BigQueryListTablesRequest,
) -> BigQueryListTablesResponse:
    """
    List all tables in a BigQuery dataset.

    Args:
        request (BigQueryListTablesRequest): The request object containing dataset_name and project_id.

    Returns:
        BigQueryListTablesResponse: A list of table IDs.
    """
    dataset_name = request.dataset_name
    logger.info(f"Listing tables in dataset {dataset_name}...")
    project_id = request.project_id

    tables = list_dataset_tables(dataset_name, project_id)
    logger.info(f"Found {len(tables)} tables")
    return BigQueryListTablesResponse(
        project_id=project_id,
        dataset_name=dataset_name,
        tables=tables,
        total_tables=len(tables),
    )


def get_bq_table_schema(
    request: BigQueryGetSchemaRequest,
) -> BigQueryTableSchema:
    """
    Get the schema of a BigQuery table.

    Args:
        request (BigQueryGetSchemaRequest): The request object containing table_name, dataset_name, and project_id.

    Returns:
        BigQueryTableSchema: The schema of the table.
    """
    table_name = request.table_name
    dataset_name = request.dataset_name
    project_id = request.project_id

    logger.info(f"Getting schema for table {table_name}...")

    # utils.get_table_schema returns list of google.cloud.bigquery.schema.SchemaField
    schema_fields_objects = get_table_schema(table_name, dataset_name, project_id)

    return BigQueryTableSchema(
        table_name=request.table_name,
        dataset_name=request.dataset_name,
        project_id=request.project_id,
        fields=schema_fields_objects,
    )


def execute_bq_query(
    request: BigQueryExecuteQueryRequest,
) -> BigQueryExecuteQueryResponse:
    """
    Execute a read-only query in BigQuery and return the results as a list of dictionaries.

    Args:
        request (BigQueryExecuteQueryRequest): The request object containing the query.

    Returns:
        BigQueryExecuteQueryResponse: A list of dictionaries representing the rows returned by the query.
    """
    query = request.query
    logger.info(f"Executing query: {query}")
    forbidden_keywords = [
        "INSERT",
        "UPDATE",
        "DELETE",
        "DROP",
        "ALTER",
        "CREATE",
        "MERGE",
        "TRUNCATE",
    ]
    upper_query = query.upper()
    for keyword in forbidden_keywords:
        if re.search(rf"\b{keyword}\b", upper_query):
            logger.warning(f"Query contains forbidden keyword: {keyword}")
            raise ValueError(
                f"Only read-only queries are allowed. Forbidden: {keyword}"
            )

    try:
        row_iterator = query_data(query)
        # Convert Row objects to dictionaries
        results = [dict(row) for row in row_iterator]
        logger.info(f"Query returned {len(results)} rows")

        return BigQueryExecuteQueryResponse(
            results=results,
            query=query,
        )
    except Exception as e:
        logger.error(f"An error occurred while executing the query: {e}")
        return BigQueryExecuteQueryResponse(
            results=[],
            query=query,
        )
