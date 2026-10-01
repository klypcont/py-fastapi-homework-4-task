import os
from pathlib import Path
from pydantic_settings import BaseSettings, SettingsConfigDict

def find_movies_csv() -> str:
    root = Path(__file__).resolve().parent.parent
    seed_path = root / "database" / "seed_data" / "imdb_movies.csv"
    if seed_path.is_file():
        return str(seed_path.resolve())
    for file_path in root.rglob("movies.csv"):
        if file_path.is_file():
            return str(file_path.resolve())
    return str(seed_path.resolve())

class BaseAppSettings(BaseSettings):
    PATH_TO_DB: str = "test.db"
    PATH_TO_MOVIES_CSV: str = find_movies_csv()

    SECRET_KEY_ACCESS: str = "test_secret_key_access_1234567890"
    SECRET_KEY_REFRESH: str = "test_secret_key_refresh_1234567890"
    JWT_SIGNING_ALGORITHM: str = "HS256"
    LOGIN_TIME_DAYS: int = 7
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    REFRESH_TOKEN_EXPIRE_DAYS: int = 7

    S3_STORAGE_ENDPOINT: str = "http://localhost:9000"
    S3_STORAGE_ACCESS_KEY: str = "test"
    S3_STORAGE_SECRET_KEY: str = "test"
    S3_STORAGE_BUCKET: str = "test-bucket"
    S3_STORAGE_BUCKET_NAME: str = "test-bucket"

    S3_ACCESS_KEY: str = "test"
    S3_SECRET_KEY: str = "test"
    S3_ENDPOINT_URL: str = "http://localhost:9000"
    S3_BUCKET_NAME: str = "test-bucket"

    EMAIL_HOST: str = "smtp.gmail.com"
    EMAIL_PORT: int = 587
    EMAIL_HOST_USER: str = "test@example.com"
    EMAIL_HOST_PASSWORD: str = "password"
    EMAIL_USE_TLS: bool = True

    SMTP_HOST: str = "smtp.gmail.com"
    SMTP_PORT: int = 587
    SMTP_USER: str = "test@example.com"
    SMTP_PASSWORD: str = "password"

    MAILHOG_HOST: str = "localhost"
    MAILHOG_API_PORT: int = 8025

    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

class Settings(BaseAppSettings):
    pass

class TestingSettings(BaseAppSettings):
    pass

settings = Settings()

PATH_TO_DB = settings.PATH_TO_DB
PATH_TO_MOVIES_CSV = settings.PATH_TO_MOVIES_CSV
SECRET_KEY_ACCESS = settings.SECRET_KEY_ACCESS
SECRET_KEY_REFRESH = settings.SECRET_KEY_REFRESH
JWT_SIGNING_ALGORITHM = settings.JWT_SIGNING_ALGORITHM
LOGIN_TIME_DAYS = settings.LOGIN_TIME_DAYS

S3_STORAGE_ENDPOINT = settings.S3_STORAGE_ENDPOINT
S3_STORAGE_ACCESS_KEY = settings.S3_STORAGE_ACCESS_KEY
S3_STORAGE_SECRET_KEY = settings.S3_STORAGE_SECRET_KEY
S3_STORAGE_BUCKET = settings.S3_STORAGE_BUCKET
S3_STORAGE_BUCKET_NAME = settings.S3_STORAGE_BUCKET_NAME

S3_ACCESS_KEY = settings.S3_ACCESS_KEY
S3_SECRET_KEY = settings.S3_SECRET_KEY
S3_ENDPOINT_URL = settings.S3_ENDPOINT_URL
S3_BUCKET_NAME = settings.S3_BUCKET_NAME

EMAIL_HOST = settings.EMAIL_HOST
EMAIL_PORT = settings.EMAIL_PORT
EMAIL_HOST_USER = settings.EMAIL_HOST_USER
EMAIL_HOST_PASSWORD = settings.EMAIL_HOST_PASSWORD
EMAIL_USE_TLS = settings.EMAIL_USE_TLS

SMTP_HOST = settings.SMTP_HOST
SMTP_PORT = settings.SMTP_PORT
SMTP_USER = settings.SMTP_USER
SMTP_PASSWORD = settings.SMTP_PASSWORD

MAILHOG_HOST = settings.MAILHOG_HOST
MAILHOG_API_PORT = settings.MAILHOG_API_PORT

def get_settings():
    return settings
