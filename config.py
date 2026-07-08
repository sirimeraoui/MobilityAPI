from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    HOST : str
    PORT : int
    DB : str
    DB_USER : str
    PASSWORD : str
    model_config = SettingsConfigDict(
        env_file=".env",
        extra="ignore"
    )

Config = Settings()