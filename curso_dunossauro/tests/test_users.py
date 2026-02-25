from http import HTTPStatus

from curso_dunossauro.schemas import UserPublic


def test_create_user(client):
    """
    Criar usuário novo, com email e username únicos.
    returns: CREATED.
    """
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


def test_create_user_username_integrity_error(client, user):
    """
    Criar usuário com username já existente.
    returns: CONFLICT.
    """
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


def test_create_user_email_integrity_error(client, user):
    """
    Criar usuário com email já existente.
    returns: CONFLICT.
    """
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


def test_get_users(client, user, token):
    """
    Obter todos os usuários, possuindo ao menos um usuário.
    returns: OK
    """
    user_schema = UserPublic.model_validate(user).model_dump()
    response = client.get(
        '/users', headers={'Authorization': f'Bearer {token}'}
    )

    assert response.status_code == HTTPStatus.OK
    assert response.json() == [user_schema]


def test_get_users_by_id(client, user):
    """
    Obter um único usuário por seu id.
    returns: OK
    """
    user_schema = UserPublic.model_validate(user).model_dump()
    response = client.get('/users/1')

    assert response.status_code == HTTPStatus.OK
    assert response.json() == user_schema


def test_get_users_by_invalid_id(client):
    """
    Tentar obter usuário por um id inválido.
    Returns: NOT FOUND
    """
    response = client.get('/users/-1')

    assert response.status_code == HTTPStatus.NOT_FOUND


def test_update_user(client, user, token):
    """
    Atualiza um usuário completo, com seus dados e id informado.
    Returns: OK
    """
    response = client.put(
        '/users/1',
        headers={'Authorization': f'Bearer {token}'},
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


def test_update_integrity_user_error(client, user, token):
    """
    Testa atualizar email para algum email já existente.
    returns: CONFLICT
    """
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
        headers={'Authorization': f'Bearer {token}'},
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


def test_update_different_user(client, token):
    """
    Testa o update quando o user é diferente do obtido pelo token.
    returns: FORBIDDEN
    """
    client.post(
        '/users',
        json={
            'username': 'UserTeste1',
            'email': 'user_teste1@hotmail.com',
            'password': 'pwdTeste1',
        },
    )
    response = client.put(
        '/users/2',
        headers={'Authorization': f'Bearer {token}'},
        json={
            'username': 'UserTeste1',
            'email': 'meu_email10@gmail.com',
            'password': 'pwd10',
        },
    )

    assert response.status_code == HTTPStatus.FORBIDDEN
    assert response.json() == {'detail': 'Not enough permission'}


def test_delete_user(client, user, token):
    """
    Testa deleção do próprio usuário obtido pelo token.
    returns: OK
    """
    response = client.delete(
        f'/users/{user.id}',
        headers={'Authorization': f'Bearer {token}'},
    )

    assert response.status_code == HTTPStatus.OK
    assert response.json() == {'message': 'User Deleted'}


def test_delete_different_user(client, token):
    """
    Testa deleção de um usuário por outro.
    returns: FORBIDDEN
    """
    client.post(
        '/users',
        json={
            'username': 'UserTeste1',
            'email': 'user_teste1@hotmail.com',
            'password': 'pwdTeste1',
        },
    )
    response = client.delete(
        '/users/2',
        headers={'Authorization': f'Bearer {token}'},
    )

    assert response.status_code == HTTPStatus.FORBIDDEN
    assert response.json() == {'detail': 'Not enough permission'}
