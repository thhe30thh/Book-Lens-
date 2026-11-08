import os


class Config:
    SECRET_KEY = os.environ.get(
        "BOOKLENS_SECRET_KEY",
        "dev-only-change-this-secret"
    )

    BOOKLENS_ENV = "development"
    DEBUG = False
    TESTING = False


class DevelopmentConfig(Config):
    DEBUG = True


class TestingConfig(Config):
    BOOKLENS_ENV = "testing"
    TESTING = True
    SECRET_KEY = "test-secret-key"


class ProductionConfig(Config):
    BOOKLENS_ENV = "production"
    DEBUG = False


CONFIGS = {
    "development": DevelopmentConfig,
    "testing": TestingConfig,
    "production": ProductionConfig,
}


def get_config(name=None):
    environment = name or os.environ.get(
        "BOOKLENS_ENV",
        "development"
    )

    if environment not in CONFIGS:
        raise ValueError(
            f"Unknown BookLens environment: {environment}"
        )

    return CONFIGS[environment]
