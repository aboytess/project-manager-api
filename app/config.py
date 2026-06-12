import os
from datetime import timedelta
from dotenv import load_dotenv
from sqlalchemy.pool import NullPool, StaticPool

load_dotenv()


class Config:
    SECRET_KEY = os.environ.get("SECRET_KEY", "dev-secret-key")
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    JWT_SECRET_KEY = os.environ.get("JWT_SECRET_KEY", "jwt-dev-secret")
    JWT_ACCESS_TOKEN_EXPIRES = timedelta(hours=1)
    JWT_REFRESH_TOKEN_EXPIRES = timedelta(days=30)


class DevelopmentConfig(Config):
    DEBUG = True
    SQLALCHEMY_DATABASE_URI = os.environ.get("DATABASE_URL", "sqlite:///dev.db")


class ProductionConfig(Config):
    DEBUG = False
    SQLALCHEMY_DATABASE_URI = os.environ.get("DATABASE_URL")


def _test_engine_options() -> dict:
    url = os.environ.get("TEST_DATABASE_URL", "sqlite:///:memory:")
    if url.startswith("sqlite"):
        return {"poolclass": StaticPool, "connect_args": {"check_same_thread": False}}
    return {"poolclass": NullPool}


class TestingConfig(Config):
    TESTING = True
    SQLALCHEMY_DATABASE_URI = os.environ.get("TEST_DATABASE_URL", "sqlite:///:memory:")
    SQLALCHEMY_ENGINE_OPTIONS = _test_engine_options()
