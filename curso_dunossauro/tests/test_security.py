from http import HTTPStatus


def test_get_token(client, user):
    response = client.post(
        '/token',
        # Utilizar o clean_password:
        # faz referência ao clean_password de conftest
        # na fixture de user. Isto cria somente em tempo de execução, para
        # enviar a senha padrão, não criptografada
        data={'username': user.email, 'password': user.clean_password},
    )
    token = response.json()

    assert response.status_code == HTTPStatus.OK
    assert 'access_token' in token
    assert 'token_type' in token


def test_jwt_invalid_token(client):
    response = client.delete(
        '/users/1', headers={'Authorization': 'Bearer token-invalido'}
    )
    assert response.status_code == HTTPStatus.UNAUTHORIZED
    assert response.json() == {'detail': 'Could not validate credentials'}


def test_jwt_token_with_blank_sub(client):
    token = (
        'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.'
        # "sub": ""
        'eyJzdWIiOiIifQ.'
        'zmTCd64SGKT1_zUnOmv-OHdd46N8blalPdUPDpWJiPw'
    )
    response = client.delete(
        '/users/1', headers={'Authorization': f'Bearer {token}'}
    )
    assert response.status_code == HTTPStatus.UNAUTHORIZED
    assert response.json() == {'detail': 'Could not validate credentials'}


def test_jwt_token_without_sub(client):
    token = (
        'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.'
        # "email": "meu_email1@meuemail.com"
        'eyJlbWFpbCI6Im1ldV9lbWFpbDFAbWV1ZW1haWwuY29tIn0.'
        'oRU7lJcbc4va0U-OJjgqFXk1DVGb2h3P9mwZ1vva5pM'
    )
    response = client.delete(
        '/users/1', headers={'Authorization': f'Bearer {token}'}
    )
    assert response.status_code == HTTPStatus.UNAUTHORIZED
    assert response.json() == {'detail': 'Could not validate credentials'}


def test_jwt_token_invalid_email(client):
    token = (
        'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.'
        # "sub": "pexe1@hotmail.com"
        'eyJzdWIiOiJwZXhlMUBob3RtYWlsLmNvbSJ9.'
        'R66wzPm5tHQ92hPZkilxTVSZJS7jVu8jv9dIGpc33RY'
    )
    response = client.delete(
        '/users/1', headers={'Authorization': f'Bearer {token}'}
    )
    # breakpoint()
    assert response.status_code == HTTPStatus.UNAUTHORIZED
    assert response.json() == {'detail': 'Could not validate credentials'}
