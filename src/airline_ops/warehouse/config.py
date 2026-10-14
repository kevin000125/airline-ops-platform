import os
from dataclasses import dataclass

from dotenv import load_dotenv


@dataclass(frozen=True)
class WarehouseConfig:
    host: str
    port: int
    database: str
    user: str
    password: str

    @classmethod
    def from_env(cls) -> "WarehouseConfig":
        load_dotenv()
        return cls(
            host=os.getenv("POSTGRES_HOST", "localhost"),
            port=int(os.getenv("POSTGRES_PORT", "5432")),
            database=os.getenv("POSTGRES_DB", "airline_ops"),
            user=os.getenv("POSTGRES_USER", "airline_user"),
            password=_required_env("POSTGRES_PASSWORD"),
        )


def _required_env(name: str) -> str:
    value = os.getenv(name)
    if not value:
        raise ValueError(f"missing required environment variable: {name}")
    return value
