from pydantic_settings import BaseSettings

class DofConfig(BaseSettings):
    PROJECT_ID: str = "mock_project_id"
    DATASET_NAME: str = "lawyer_agent"
    TABLE_NAME: str = "dof"

settings = DofConfig()
