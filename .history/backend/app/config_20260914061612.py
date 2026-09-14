from functools import lru_cache
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    # --- MySQL connection ---
    DB_USER: str = "ug0upavxz7lnuapc"
    DB_PASSWORD: str = "gRv63QNE5sKjPmyYHlcx"
    DB_HOST: str = "broxjkrxm0sh2okbsk9e-mysql.services.clever-cloud.com"
    DB_PORT: str = "3306"
    DB_NAME: str = "broxjkrxm0sh2okbsk9e"

    # --- JWT ---
    JWT_SECRET_KEY: str = "dev-secret-change-me"
    JWT_ACCESS_TOKEN_EXPIRE_HOURS: int = 8

    # --- CORS --- (comma-separated list of allowed frontend origins)
    CORS_ORIGINS: str = "http://localhost:3000,http://"

    @property
    def sqlalchemy_database_uri(self) -> str:
        return f"mysql+pymysql://{self.DB_USER}:{self.DB_PASSWORD}@{self.DB_HOST}:{self.DB_PORT}/{self.DB_NAME}"

    @property
    def cors_origins_list(self) -> list[str]:
        return [origin.strip() for origin in self.CORS_ORIGINS.split(",")]


@lru_cache
def get_settings() -> Settings:
    return Settings()
