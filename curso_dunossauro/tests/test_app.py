from http import HTTPStatus

# from fastapi.testclient import TestClient

# from curso_dunossauro.app import app


# def test_root_deve_retornar_ok_e_ola_mundo():  - Forma HardCoding
#     client = TestClient(app)  # Arrange
# Forma correta:
def test_root_deve_retornar_ok_e_ola_mundo(client):
    response = client.get('/')  # Act

    assert response.status_code == HTTPStatus.OK  # Assert
    assert response.json() == {'message': 'Olá Mundo!'}  # Asset


def test_html_page(client):

    response = client.get('/html')  # Act

    assert response.status_code == HTTPStatus.OK
    assert 'Olá Mundo' in response.text


# def test_create_user(): - Forma HardCoding
# client = TestClient(app)


def test_create_user(client):
    response = client.post(
        '/users',
        json={
            'username': 'meu_user1',
            'email': 'meu_email1@gmail.com',
            'password': 'pwd1',
        },
    )

    assert response.status_code == HTTPStatus.CREATED
    assert response.json() == {
        'id': 1,
        'email': 'meu_email1@gmail.com',
        'username': 'meu_user1',
    }


def test_get_users(client):
    response = client.get('/users')

    assert response.status_code == HTTPStatus.OK
    assert response.json() == [
        {'id': 1, 'email': 'meu_email1@gmail.com', 'username': 'meu_user1'}
    ]


def test_get_users_by_id(client):
    response = client.get('/users/1')

    assert response.status_code == HTTPStatus.OK
    assert response.json() == {
        'id': 1,
        'email': 'meu_email1@gmail.com',
        'username': 'meu_user1',
    }


def test_get_users_by_invalid_id(client):
    response = client.get('/users/-1')

    assert response.status_code == HTTPStatus.NOT_FOUND


def test_update_user(client):
    response = client.put(
        '/users/1',
        json={
            'username': 'meu_user10',
            'email': 'meu_email10@gmail.com',
            'password': 'pwd10',
        },
    )

    assert response.status_code == HTTPStatus.OK
    assert response.json() == {
        'id': 1,
        'email': 'meu_email10@gmail.com',
        'username': 'meu_user10',
    }


def test_update_user_invalid_id(client):
    response = client.put(
        '/users/-10',
        json={
            'username': 'meu_user10',
            'email': 'meu_email10@gmail.com',
            'password': 'pwd10',
        },
    )

    assert response.status_code == HTTPStatus.NOT_FOUND


def test_delete_user(client):
    response = client.delete('/users/1')

    assert response.status_code == HTTPStatus.OK
    assert response.json() == {
        'id': 1,
        'email': 'meu_email10@gmail.com',
        'username': 'meu_user10',
    }


def test_delete_user_invalid_id(client):
    response = client.delete('/users/-10')

    assert response.status_code == HTTPStatus.NOT_FOUND
