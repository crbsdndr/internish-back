import os

from dotenv import load_dotenv
from pydantic_settings import BaseSettings

load_dotenv()

class ConfigDatabase:
    db_host: str = os.getenv("DB_HOST")
    db_name: str = os.getenv("DB_NAME")
    db_user: str = os.getenv("DB_USER")
    db_password: str = os.getenv("DB_PASSWORD")
    db_port: str = os.getenv("DB_PORT")


class ConfigJWT(BaseSettings):
    JWT_SECRET: str = os.getenv("JWT_SECRET")
    JWT_ALG: str = os.getenv("JWT_ALG")
    ACCESS_EXPIRE_MIN: int = os.getenv("ACCESS_EXPIRE_MIN")
    REFRESH_EXPIRE_MIN: int = os.getenv("REFRESH_EXPIRE_MIN")

    class Config:
        env_file = ".env"
        extra = "ignore"

config_database = ConfigDatabase()
config_jwt = ConfigJWT()