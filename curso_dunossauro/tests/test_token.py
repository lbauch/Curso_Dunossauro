from http import HTTPStatus

from freezegun import freeze_time
from jwt import decode


def test_create_token(client, user, settings):
    """
    Cria token com usuário e senha corretos.
    returns: OK
    """
    response = client.post(
        '/auth/token',
        data={'username': user.email, 'password': user.clean_password},
    )
    token = response.json()

    assert response.status_code == HTTPStatus.OK
    assert 'access_token' in token
    assert 'token_type' in token
    access_token = token['access_token']
    token_data = decode(
        access_token, key=settings.SECRET_KEY, algorithms=settings.ALGORITHM
    )
    assert 'exp' in token_data


def test_get_token_invalid_username(client, user):
    """
    Tenta criar token com email não existente.
    returns: UNAUTHORIZED
    """
    response = client.post(
        '/auth/token',
        data={
            'username': 'algum_emailqualquer@hotmail.com',
            'password': user.clean_password,
        },
    )

    assert response.status_code == HTTPStatus.UNAUTHORIZED
    assert response.json() == {'detail': 'Incorrect email or password'}


def test_get_token_invalid_password(client, user):
    """
    Tenta criar um token para uma senha incorreta.
    returns: UNAUTHORIZED
    """
    response = client.post(
        '/auth/token',
        data={
            'username': user.email,
            'password': 'uma pwd errada',
        },
    )

    assert response.status_code == HTTPStatus.UNAUTHORIZED
    assert response.json() == {'detail': 'Incorrect email or password'}


def test_jwt_invalid_token(client):
    """
    Tenta utilizar um token que não pode ser decodificado corretamente.
    returns: UNAUTHORIZED
    """
    response = client.delete(
        '/users/1', headers={'Authorization': 'Bearer token-invalido'}
    )
    assert response.status_code == HTTPStatus.UNAUTHORIZED
    assert response.json() == {'detail': 'Could not validate credentials'}


def test_jwt_token_with_blank_sub(client):
    """
    Tenta utilizar um token com o sub vazio.
    returns: UNAUTHORIZED
    """
    token = (
        'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.'
        # "sub": ""
        'eyJzdWIiOiIifQ.'
        'IfhRxU4g9kPOpcGjnu3Y92dcIBc37bvaFN6lWpLqxp4'
    )
    response = client.delete(
        '/users/1', headers={'Authorization': f'Bearer {token}'}
    )
    assert response.status_code == HTTPStatus.UNAUTHORIZED
    assert response.json() == {'detail': 'Could not validate credentials'}


def test_jwt_token_without_sub(client):
    """
    Tenta utilizar um token sem o campo sub no json.
    returns: UNAUTHORIZED
    """
    token = (
        'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.'
        # "email": "meu_email1@meuemail.com"
        'eyJlbWFpbCI6Im1ldV9lbWFpbDFAbWV1ZW1haWwuY29tIn0.'
        'mArmgo0zbG64jJVK1nw3d4PIW9Nhg8qYS5m-qOZcqoo'
    )
    response = client.delete(
        '/users/1', headers={'Authorization': f'Bearer {token}'}
    )
    assert response.status_code == HTTPStatus.UNAUTHORIZED
    assert response.json() == {'detail': 'Could not validate credentials'}


def test_jwt_token_invalid_email(client):
    """
    Tenta utilizar um token de um user que não exista.
    returns: UNAUTHORIZED
    """
    token = (
        'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.'
        # "sub": "pexe1@hotmail.com"
        'eyJzdWIiOiJwZXhlMUBob3RtYWlsLmNvbSJ9.'
        'Bolj7KY4sFxRzIgW1WGAzVH0NoQzhgMJNWYaZ-Z6S5g'
    )
    response = client.delete(
        '/users/1', headers={'Authorization': f'Bearer {token}'}
    )
    assert response.status_code == HTTPStatus.UNAUTHORIZED
    assert response.json() == {'detail': 'Could not validate credentials'}


def test_token_expired_after_time(client, user):
    """
    Tenta utilizar token expirado.
    returns: UNAUTHORIZED
    """
    with freeze_time('2025-12-14 12:00:00'):
        response = client.post(
            '/auth/token',
            data={
                'username': user.email,
                'password': user.clean_password,
            },
        )
        assert response.status_code == HTTPStatus.OK
        token = response.json()['access_token']

    with freeze_time('2025-12-14 12:31:00'):
        response = client.put(
            f'/users/{user.id}',
            headers={'Authorization': f'Bearer {token}'},
            json={
                'username': 'wrongwrong',
                'email': 'wrong@wrong.com',
                'password': 'wrong',
            },
        )
        assert response.status_code == HTTPStatus.UNAUTHORIZED
        assert response.json() == {'detail': 'Could not validate credentials'}


def test_refresh_token(client, token):
    """
    Renova um token que não está expirado.
    returns: OK
    """
    response = client.post(
        '/auth/refresh_token',
        headers={'Authorization': f'Bearer {token}'},
    )

    data = response.json()

    assert response.status_code == HTTPStatus.OK
    assert 'access_token' in data
    assert 'token_type' in data
    assert data['token_type'] == 'bearer'


def test_token_expired_dont_refresh(client, user):
    """
    Tenta atualizar token já expirado.
    Por mais que o teste de expiração já foi feito, é boa prática
    ter este teste também, afim de evitar erros futuros.
    returns: UNAUTHORIZED
    """
    with freeze_time('2023-07-14 12:00:00'):
        response = client.post(
            '/auth/token',
            data={'username': user.email, 'password': user.clean_password},
        )
        assert response.status_code == HTTPStatus.OK
        token = response.json()['access_token']

    with freeze_time('2023-07-14 12:31:00'):
        response = client.post(
            '/auth/refresh_token',
            headers={'Authorization': f'Bearer {token}'},
        )
        assert response.status_code == HTTPStatus.UNAUTHORIZED
        assert response.json() == {'detail': 'Could not validate credentials'}
