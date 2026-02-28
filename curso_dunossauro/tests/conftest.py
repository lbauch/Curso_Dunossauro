from contextlib import contextmanager
from datetime import datetime

import pytest
import pytest_asyncio
from fastapi.testclient import TestClient
from sqlalchemy import event
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.pool import StaticPool

from curso_dunossauro.app import app
from curso_dunossauro.database import get_session
from curso_dunossauro.models import User, table_registry
from curso_dunossauro.security import get_password_hash
from curso_dunossauro.settings import Settings


@pytest.fixture
def client(session: AsyncSession):

    def get_session_override():
        return session

    with TestClient(app) as client:
        app.dependency_overrides[get_session] = get_session_override
        return client

    app.dependency_overrides.clear()


@pytest_asyncio.fixture
async def session():
    engine = create_async_engine(
        'sqlite+aiosqlite:///:memory:',
        connect_args={'check_same_thread': False},
        poolclass=StaticPool,
    )
    # O método begin() do engine é usado para iniciar uma transação no
    # banco de dados. O engine cria uma conexão assíncrona e,
    # ao usar begin(), estamos dizendo ao SQLAlchemy para iniciar
    # uma transação dentro do contexto de execução assíncrona.
    # Ele é necessário para que possamos executar operações no
    # banco de dados de forma eficiente e transacional.
    async with engine.begin() as conn:
        # O run_sync é uma forma de rodar código síncrono dentro de
        # um ambiente assíncrono. No caso do SQLAlchemy, ele é usado
        # para executar operações que não são assíncronas
        # (como a criação de tabelas) enquanto ainda estamos
        # entro do loop de eventos assíncrono.
        await conn.run_sync(table_registry.metadata.create_all)

    async with AsyncSession(engine, expire_on_commit=False) as session:
        yield session

    async with engine.begin() as conn:
        await conn.run_sync(table_registry.metadata.drop_all)


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


@pytest_asyncio.fixture
async def user(session: AsyncSession):
    password = 'minhaSenha1'
    user = User(
        username='meu_username1',
        email='meu_email1@meuemail.com',
        password=get_password_hash(password),
    )
    session.add(user)
    await session.commit()
    await session.refresh(user)

    # Mantém a senha limpa em tempo de execução.
    # Útil para testar a geração do token em teste_app::test_get_token
    user.clean_password = password

    return user


@pytest.fixture
def token(client, user):
    response = client.post(
        '/auth/token',
        data={'username': user.email, 'password': user.clean_password},
    )
    return response.json()['access_token']


@pytest.fixture
def settings():
    return Settings()
