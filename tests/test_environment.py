def test_environment_imports() -> None:
    import dotenv
    import pandas
    import pyarrow

    assert pandas is not None
    assert pyarrow is not None
    assert dotenv is not None
