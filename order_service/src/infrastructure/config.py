from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    database_host: str
    database_port: int
    database_user: str
    database_password: str
    database_name: str

    model_config = SettingsConfigDict(env_file=".env")


settings = Settings()
