from sqlalchemy import create_engine
from sqlalchemy.engine import Engine


class DatabaseConnector:
    _instance = None
    _engine = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(DatabaseConnector, cls).__new__(cls)
        return cls._instance

    def __init__(self):
        if self._engine is None:
            from api.config import settings
            self._engine = create_engine(
                settings.database_url,
                pool_pre_ping=True,
                echo=False
            )

    @property
    def engine(self) -> Engine:
        return self._engine

    def close(self):
        if self._engine:
            self._engine.dispose()
