from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import Field
from typing import Annotated


class BQConfig(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
        validate_assignment=True,
    )
    """
    Class that holds configuration values for GCP services. Allowing to, in any future, change the
    cloud provider or the way to access the secrets.
    """

    PROJECT_ID: Annotated[
        str,
        Field(
            default="dummy-gcp-project-id",
            description="GCP Project ID",
        ),
    ]
    PUBLIC_GCP_PROJECT: Annotated[
        str,
        Field(
            default="bigquery-public-data",
            description="GCP Project ID",
        ),
    ]
