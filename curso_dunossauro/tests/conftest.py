import pytest
from fastapi.testclient import TestClient

from curso_dunossauro.app import app


@pytest.fixture
def client():
    return TestClient(app)
