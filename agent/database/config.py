from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import Field
from typing import Annotated


class DBConfig(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env", env_file_encoding="utf-8", extra="ignore"
    )
    PROJECT_ID: Annotated[
        str,
        Field(
            default="dummy-gcp-project-id",
            description="GCP Project ID",
        ),
    ]
    AGENT_DATASET: Annotated[
        str,
        Field(
            default="dummy-dataset",
            description="Dataset containing all the agent conversations",
        ),
    ]
    CONVERSATIONS_TABLE_NAME: Annotated[
        str,
        Field(
            description="Name of the BQ table",
            default="conversations",
        ),
    ]
    CONVERSATIONS_TABLE_PK: Annotated[
        str,
        Field(
            description="PK of the BQ table",
            default="prompt_id",
        ),
    ]
    USERS_TABLE_NAME: Annotated[
        str,
        Field(
            description="Name of the Users BQ table",
            default="users",
        ),
    ]
    USERS_TABLE_PK: Annotated[
        str,
        Field(
            description="PK of the Users BQ table",
            default="user_id",
        ),
    ]
