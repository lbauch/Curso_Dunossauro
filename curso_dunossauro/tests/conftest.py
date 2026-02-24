from contextlib import contextmanager
from datetime import datetime

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine, event
from sqlalchemy.orm import Session
from sqlalchemy.pool import StaticPool

from curso_dunossauro.app import app
from curso_dunossauro.database import get_session
from curso_dunossauro.models import User, table_registry
from curso_dunossauro.security import get_password_hash


@pytest.fixture
def client(session):

    def get_session_override():
        return session

    with TestClient(app) as client:
        app.dependency_overrides[get_session] = get_session_override
        return client

    app.dependency_overrides.clear()


@pytest.fixture
def session():
    engine = create_engine(
        'sqlite:///:memory:',
        connect_args={'check_same_thread': False},
        poolclass=StaticPool,
    )
    table_registry.metadata.create_all(engine)

    with Session(engine) as session:
        yield session

    table_registry.metadata.drop_all(engine)
    engine.dispose()


@contextmanager
# Utilizado como hook.
# created_at somente é gerado no banco. Precisa de um suporte para validá-lo.
def _mock_db_time(*, model=User, time=datetime(2025, 5, 20)):
    def fake_insert_time_hook(mapper, connection, target):
        if hasattr(target, 'created_at'):
            target.created_at = time
        if hasattr(target, 'updated_at'):
            target.updated_at = time

    def fake_update_time_hook(mapper, connection, target):
        if hasattr(target, 'updated_at'):
            target.updated_at = time

    event.listen(model, 'before_insert', fake_insert_time_hook)
    event.listen(model, 'before_update', fake_update_time_hook)

    yield time

    event.remove(model, 'before_insert', fake_insert_time_hook)
    event.remove(model, 'before_update', fake_update_time_hook)


@pytest.fixture
def mock_db_time():
    return _mock_db_time


@pytest.fixture
def user(session):
    password = 'minhaSenha1'
    user = User(
        username='meu_username1',
        email='meu_email1@meuemail.com',
        password=get_password_hash(password),
    )
    session.add(user)
    session.commit()
    session.refresh(user)

    # Mantém a senha limpa em tempo de execução.
    # Útil para testar a geração do token em teste_app::test_get_token
    user.clean_password = password

    return user


@pytest.fixture
def token(client, user):
    response = client.post(
        '/token',
        data={'username': user.email, 'password': user.clean_password},
    )
    return response.json()['access_token']
