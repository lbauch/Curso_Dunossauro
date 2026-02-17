from http import HTTPStatus

from fastapi.testclient import TestClient

from curso_dunossauro.app import app


def test_root_deve_retornar_ok_e_ola_mundo():
    client = TestClient(app)  # Arrange

    response = client.get("/")  # Act

    assert response.status_code == HTTPStatus.OK  # Assert
    assert response.json() == {"message": "Olá Mundo!"}  # Asset


def test_html_page():
    client = TestClient(app)  # Arrange

    response = client.get("/html")  # Act

    assert response.status_code == HTTPStatus.OK
    assert "Olá Mundo" in response.text
