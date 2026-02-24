from http import HTTPStatus

from curso_dunossauro.schemas import UserPublic


def test_root_deve_retornar_ok_e_ola_mundo(client):
    response = client.get('/')  # Act

    assert response.status_code == HTTPStatus.OK  # Assert
    assert response.json() == {'message': 'Olá Mundo!'}  # Asset


def test_html_page(client):

    response = client.get('/html')  # Act

    assert response.status_code == HTTPStatus.OK
    assert 'Olá Mundo' in response.text


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


def test_create_user_username_integrity(client, user):
    response = client.post(
        '/users',
        json={
            'username': 'meu_username1',
            'email': 'meu_email2@gmail.com',
            'password': 'pwd1',
        },
    )

    assert response.status_code == HTTPStatus.CONFLICT
    assert response.json() == {
        'detail': 'User with given email or username already exists.'
    }


def test_create_user_email_integrity(client, user):
    response = client.post(
        '/users',
        json={
            'username': 'meu_user1',
            'email': 'meu_email1@meuemail.com',
            'password': 'pwd1',
        },
    )

    assert response.status_code == HTTPStatus.CONFLICT
    assert response.json() == {
        'detail': 'User with given email or username already exists.'
    }


def test_get_users(client):
    response = client.get('/users')

    assert response.status_code == HTTPStatus.OK
    assert response.json() == []


def test_get_users_with_user(client, user):
    user_schema = UserPublic.model_validate(user).model_dump()
    response = client.get('/users')

    assert response.status_code == HTTPStatus.OK
    assert response.json() == [user_schema]


def test_get_users_by_id(client, user):
    user_schema = UserPublic.model_validate(user).model_dump()
    response = client.get('/users/1')

    assert response.status_code == HTTPStatus.OK
    assert response.json() == user_schema


def test_get_users_by_invalid_id(client):
    response = client.get('/users/-1')

    assert response.status_code == HTTPStatus.NOT_FOUND


def test_update_user(client, user):
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


def test_update_integrity_user(client, user):
    client.post(
        '/users',
        json={
            'username': 'UserTeste1',
            'email': 'user_teste1@hotmail.com',
            'password': 'pwdTeste1',
        },
    )
    response = client.put(
        f'/users/{user.id}',
        json={
            'username': 'UserTeste1',
            'email': 'meu_email10@gmail.com',
            'password': 'pwd10',
        },
    )

    assert response.status_code == HTTPStatus.CONFLICT
    assert response.json() == {
        'detail': 'User with given email or username already exists.'
    }


def test_delete_user(client, user):
    response = client.delete('/users/1')

    assert response.status_code == HTTPStatus.OK
    assert response.json() == {'message': 'User Deleted'}


def test_delete_user_invalid_id(client):
    response = client.delete('/users/-10')

    assert response.status_code == HTTPStatus.NOT_FOUND
