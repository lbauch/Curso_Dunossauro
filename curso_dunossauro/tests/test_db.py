from dataclasses import asdict
from datetime import datetime

import pytest
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from curso_dunossauro.models import User


@pytest.mark.asyncio
async def test_create_user(session: AsyncSession, mock_db_time):
    """
    Testa a criação do usuário no banco e valida conexão com banco.
    """
    with mock_db_time(model=User, time=datetime.now()) as time:
        new_user = User(
            username='teste', email='teste@teste.com', password='senha1'
        )

        session.add(new_user)
        await session.commit()

        user = await session.scalar(  # Converte valor em objeto python
            select(User).where(User.username == 'teste')
        )

        assert asdict(user) == {
            'id': 1,
            'username': 'teste',
            'email': 'teste@teste.com',
            'password': 'senha1',
            'created_at': time,
            'updated_at': time,
            'todos': [],
        }


@pytest.mark.asyncio
async def test_update_user(session: AsyncSession, mock_db_time):
    """
    Testa a atualização do usuário no banco e valida conexão com banco.
    """
    initial_time = datetime(2025, 5, 20)
    updated_time = datetime(2025, 5, 21)

    # Criação
    with mock_db_time(model=User, time=initial_time):
        user = User(
            username='teste',
            email='teste@teste.com',
            password='senha1',
        )
        session.add(user)
        await session.commit()

    # Atualização
    with mock_db_time(model=User, time=updated_time):
        user.username = 'teste2'
        await session.commit()

    await session.refresh(user)

    assert user.username == 'teste2'
    assert user.created_at == initial_time
    assert user.updated_at == updated_time
