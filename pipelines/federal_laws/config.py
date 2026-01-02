from pydantic_settings import BaseSettings

class ScraperSettings(BaseSettings):
    PROJECT_ID: str = "learned-stone-454021-c8"
    BUCKET_NAME: str = "lawyer_agent"
    GCS_FOLDER: str = "federal_laws"
    URL: str = "https://www.diputados.gob.mx/LeyesBiblio/index.htm"
    BASE_URL: str = "https://www.diputados.gob.mx/LeyesBiblio/"
    MAX_WORKERS: int = 5

settings = ScraperSettings()