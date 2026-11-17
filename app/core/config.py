
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    database_url: str
    digicoc_jwt_secret: str

    digicoc_biometric_encryption_key: str
    digicoc_biometric_encryption_key_version: str = "v1"

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )


settings = Settings()
