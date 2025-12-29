from google.cloud import bigquery
from typing import Literal
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


def insert_rows_from_json(
    table_name: str,
    dataset_name: str,
    project_id: str,
    rows: list[dict],
    write_disposition: Literal[
        "WRITE_APPEND", "WRITE_TRUNCATE", "WRITE_EMPTY"
    ] = "WRITE_APPEND",
    create_disposition: Literal[
        "CREATE_IF_NEEDED", "CREATE_NEVER"
    ] = "CREATE_NEVER",
) -> None:
    """
    Insert rows into a table in BigQuery. This function does not pass it through the streaming buffer, allowing ease of update, and deletion.
    Code adapted from: https://docs.cloud.google.com/python/docs/reference/bigquery/latest/google.cloud.bigquery.client.Client#google_cloud_bigquery_client_Client_load_table_from_json

    Args:
        table_name: str -> The name of the table to insert rows into.
        dataset_name: str -> The name of the dataset where the table is located.
        project_id: str -> The project ID where the dataset is located.
        write_disposition: str ->  Specifies the action that occurs if destination table already exists. Default: WRITE_APPEND
        rows (list[dict]): A list of dictionaries representing the rows to insert. Ex:

                    [
                        {
                            "column_name": "value",
                            "column_name2": 123,
                            "column_name3": 123.45,
                            "column_name4": "2023-10-01T00:00:00Z"
                        },
                        {
                            "column_name": "value2",
                            "column_name2": 456,
                            "column_name3": 678.90,
                            "column_name4": "2023-10-02T00:00:00Z"
                        }
                    ]

    Returns:
        None
    """
    # table_exists already has error handlers for its parameters
    if not table_exists(table_name, dataset_name, project_id):
        raise ValueError(
            f"Table {table_name} does not exist in dataset {dataset_name}."
        )

    table_id = f"{project_id}.{dataset_name}.{table_name}"

    job_config = bigquery.LoadJobConfig(
        write_disposition=write_disposition,
        create_disposition=create_disposition,
    )

    try:
        load_job = client.load_table_from_json(
            destination=table_id,
            json_rows=rows,
            job_config=job_config,
        )

        # Start the job and wait for it to complete and get the result
        # Check documentation: https://docs.cloud.google.com/python/docs/reference/bigquery/latest/google.cloud.bigquery.job.LoadJob#google_cloud_bigquery_job_LoadJob_errors
        load_job.result()

        if load_job.error_result:
            logger.exception("There was an error during the load to the BigQuery table")
            raise ValueError(
                f"Errors occurred while inserting rows: {load_job.error_result}"
            )

        logger.info(f"Rows successfully inserted into {table_name}.")
    except Exception as e:
        raise ValueError(f"Error inserting rows: {e}")