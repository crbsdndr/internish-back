import os

from dotenv import load_dotenv
from pydantic_settings import BaseSettings

load_dotenv()

class ConfigDatabase(BaseSettings):
    DB_HOST: str = os.getenv("DB_HOST")
    DB_NAME: str = os.getenv("DB_NAME")
    DB_USER: str = os.getenv("DB_USER")
    DB_PASSWORD: str = os.getenv("DB_PASSWORD")
    DB_PORT: str = os.getenv("DB_PORT")

    class Config:
        env_file = ".env"
        extra = "ignore"


class ConfigJWT(BaseSettings):
    JWT_SECRET: str = os.getenv("JWT_SECRET")
    JWT_ALG: str = os.getenv("JWT_ALG")
    ACCESS_EXPIRE_MIN: int = os.getenv("ACCESS_EXPIRE_MIN")
    REFRESH_EXPIRE_MIN: int = os.getenv("REFRESH_EXPIRE_MIN")

    class Config:
        env_file = ".env"
        extra = "ignore"

class ConfigFrontend(BaseSettings):
    FRONTEND_URL: str = os.getenv("FRONTEND_URL")

    class Config:
        env_file = ".env"
        extra = "ignore"

config_database = ConfigDatabase()
config_jwt = ConfigJWT()
config_frontend = ConfigFrontend()
