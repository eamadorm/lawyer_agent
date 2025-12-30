from pydantic import BaseModel, Field, ConfigDict, field_serializer, BeforeValidator
from typing import Annotated, Any
from enum import StrEnum
from google.cloud.bigquery.schema import SchemaField
from .config import BQConfig

bq_config = BQConfig()


## Common Validators
STRING_NORMALIZER = BeforeValidator(
    lambda text: str(text).strip() if text is not None else None
)


class AllowedBQProjects(StrEnum):
    MAIN_PROJECT = bq_config.PROJECT_ID


class AllowedBQDatasets(StrEnum):
    LAWYER_AGENT = "lawyer_agent"

## Common Attributes/Fields
PROJECT_ID_FIELD = Annotated[
    AllowedBQProjects,
    Field(
        description="The GCP project ID",
    ),
]
DATASET_NAME_FIELD = Annotated[
    AllowedBQDatasets,
    Field(
        description="The name of the dataset.",
        min_length=1,
    ),
    STRING_NORMALIZER,
]
TABLE_NAME_FIELD = Annotated[
    str,
    Field(
        description="The name of the table.",
        min_length=1,
    ),
    STRING_NORMALIZER,
]


class BigQueryListDatasetsRequest(BaseModel):
    project_id: PROJECT_ID_FIELD


class BigQueryListDatasetsResponse(BigQueryListDatasetsRequest):
    datasets: Annotated[
        list[str],
        Field(description="List of dataset IDs."),
    ]
    total_datasets: Annotated[
        int,
        Field(
            description="Total number of datasets.",
            ge=0,
        ),
    ]


class BigQueryListTablesRequest(BaseModel):
    dataset_name: DATASET_NAME_FIELD
    project_id: PROJECT_ID_FIELD


class BigQueryListTablesResponse(BigQueryListTablesRequest):
    tables: Annotated[list[str], Field(description="List of table IDs.")]
    total_tables: Annotated[int, Field(description="Total number of tables.", ge=0)]


class BigQueryGetSchemaRequest(BaseModel):
    table_name: TABLE_NAME_FIELD
    dataset_name: DATASET_NAME_FIELD
    project_id: PROJECT_ID_FIELD


class BigQueryTableSchema(BigQueryGetSchemaRequest):
    model_config = ConfigDict(arbitrary_types_allowed=True)

    fields: Annotated[
        list[SchemaField],
        Field(description="The fields of the table."),
    ]

    @field_serializer("fields")
    def serialize_fields(self, fields: list[SchemaField], _info: Any) -> list[dict]:
        # to_api_repr() returns a dict representation suitable for JSON
        return [field.to_api_repr() for field in fields]


class BigQueryExecuteQueryRequest(BaseModel):
    query: Annotated[str, Field(description="The SQL query to execute.")]


class BigQueryExecuteQueryResponse(BigQueryExecuteQueryRequest):
    results: Annotated[
        list[dict], Field(description="List of rows returned by the query.")
    ]


class BigQueryExecution(BigQueryExecuteQueryResponse):
    query_id: Annotated[
        str,
        Field(
            description="Unique identifier of the executed query during an agent response",
        ),
    ]
