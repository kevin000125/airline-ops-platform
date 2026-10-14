from airline_ops.warehouse.config import WarehouseConfig


def test_warehouse_config_from_env(monkeypatch) -> None:
    monkeypatch.setenv("POSTGRES_HOST", "database")
    monkeypatch.setenv("POSTGRES_PORT", "5433")
    monkeypatch.setenv("POSTGRES_DB", "test_db")
    monkeypatch.setenv("POSTGRES_USER", "test_user")
    monkeypatch.setenv("POSTGRES_PASSWORD", "secret")

    config = WarehouseConfig.from_env()

    assert config.host == "database"
    assert config.port == 5433
    assert config.database == "test_db"
    assert config.user == "test_user"
    assert config.password == "secret"
