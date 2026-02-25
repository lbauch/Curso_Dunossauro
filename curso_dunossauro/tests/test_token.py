from http import HTTPStatus

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
    # breakpoint()
    assert response.status_code == HTTPStatus.UNAUTHORIZED
    assert response.json() == {'detail': 'Could not validate credentials'}
