import os
os.environ.setdefault("MOCK_MODE", "true")
os.environ.setdefault("DATA_DIR", "data_test")
import pytest


@pytest.fixture(autouse=True, scope="session")
def _clean_test_data():
    import shutil
    shutil.rmtree("data_test", ignore_errors=True)
    os.makedirs("data_test", exist_ok=True)
    yield
