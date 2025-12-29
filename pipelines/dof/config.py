from pydantic_settings import BaseSettings

class DofConfig(BaseSettings):
    PROJECT_ID: str = "mock_project_id"
    DATASET_NAME: str = "lawyer_agent"
    TABLE_NAME: str = "dof"
    DOF_BASE_URL: str = "https://www.dof.gob.mx/index.php"
    DOF_BASE_HOST: str = "https://www.dof.gob.mx"

settings = DofConfig()
