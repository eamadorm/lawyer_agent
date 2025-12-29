from google.cloud import bigquery
from google.cloud.bigquery.schema import SchemaField
from loguru import logger


client = bigquery.Client()


def dataset_exists(dataset_name: str, project_id: str) -> bool:
    """
    Check if a dataset exists in BigQuery.

    Args:
        dataset_name (str): The name of the dataset to check.
        project_id (str): The project ID where the dataset is located.

    Returns:
        bool: True if the dataset exists, False otherwise.
    """
    parameters = {"dataset_name": dataset_name, "project_id": project_id}
    if not all(
        [isinstance(param, str) and param != "" for param in parameters.values()]
    ):
        raise ValueError(
            f"The parameters {', '.join(parameters.keys())} must be not null strings."
        )

    dataset_id = f"{project_id}.{dataset_name}"

    try:
        client.get_dataset(dataset_id)
        return True
    except Exception as e:
        if "Not found" in str(e):
            return False
        else:
            raise e


def table_exists(table_name: str, dataset_name: str, project_id: str) -> bool:
    """
    Check if a table exists in a dataset in BigQuery.

    Args:
        table_name (str): The name of the table to check.
        dataset_name (str): The name of the dataset where the table is located.
        project_id (str): The project ID where the dataset is located.

    Returns:
        bool: True if the table exists, False otherwise.
    """
    parameters = {
        "table_name": table_name,
        "dataset_name": dataset_name,
        "project_id": project_id,
    }
    if not all(
        [isinstance(param, str) and param != "" for param in parameters.values()]
    ):
        raise ValueError(
            f"The parameters {', '.join(parameters.keys())} must be not null strings."
        )

    table_id = f"{project_id}.{dataset_name}.{table_name}"

    try:
        client.get_table(table_id)
        return True
    except Exception as e:
        if "Not found" in str(e):
            return False
        else:
            raise e


def list_datasets(project_id: str) -> list[str]:
    """
    List all datasets in a BigQuery project.

    Args:
        project_id (str): The project ID to list datasets from.

    Returns:
        list[str]: A list of dataset IDs.
    """
    try:
        datasets = list(client.list_datasets(project=project_id))
        if datasets:
            return [dataset.dataset_id for dataset in datasets]
        else:
            return []
    except Exception as e:
        logger.error(f"Error listing datasets: {e}")
        return []


def list_dataset_tables(dataset_name: str, project_id: str) -> list[str]:
    """
    Get all the tables from a dataset

    Args:
        dataset_name: The name of the dataset.
        project_id: The project ID.

    Returns:
        list[str]: A list of table names.
    """
    dataset_id = f"{project_id}.{dataset_name}"
    try:
        tables = list(client.list_tables(dataset_id))
        if tables:
            return [table.table_id for table in tables]
        else:
            return []
    except Exception as e:
        logger.error(f"Error listing tables: {e}")
        return []


def get_table_schema(
    table_name: str, dataset_name: str, project_id: str
) -> list[SchemaField]:
    """
    Get the schema of a table in BigQuery.

    Args:
        table_name (str): The name of the table.
        dataset_name (str): The name of the dataset.
        project_id (str): The project ID.

    Returns:
        list[SchemaField]: A list of SchemaField objects.
    """
    if not table_exists(table_name, dataset_name, project_id):
        raise ValueError(
            f"Table {table_name} does not exist in dataset {dataset_name}."
        )

    table_id = f"{project_id}.{dataset_name}.{table_name}"
    try:
        table = client.get_table(table_id)
        return table.schema
    except Exception as e:
        raise ValueError(f"Error getting table schema: {e}")


def query_data(query: str) -> list:
    """
    Query data from a table in BigQuery.

    Args:
        query (str): The SQL query to execute.

    Returns:
        list: A list of rows returned by the query.
    """
    if not isinstance(query, str) or query == "":
        raise ValueError("The query must be a non-empty string.")

    try:
        query_job = client.query(query)
        results = query_job.result()
        return results

    except Exception as e:
        raise ValueError(f"Error querying the data: {e}")
