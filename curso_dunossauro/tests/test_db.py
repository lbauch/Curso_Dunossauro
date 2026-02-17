from dataclasses import asdict
from datetime import datetime

from sqlalchemy import select

from curso_dunossauro.models import User


def test_create_user(session, mock_db_time):
    with mock_db_time(model=User, time=datetime.now()) as time:
        new_user = User(
            username='teste', email='teste@teste.com', password='senha1'
        )

        session.add(new_user)
        session.commit()

        user = session.scalar(  # Converte o valor em um objeto python
            select(User).where(User.username == 'teste')
        )

        assert asdict(user) == {
            'id': 1,
            'username': 'teste',
            'email': 'teste@teste.com',
            'password': 'senha1',
            'created_at': time,
            'updated_at': time,
        }
    # assert user.id == 1


def test_update_user(session, mock_db_time):
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
        session.commit()

    # Atualização
    with mock_db_time(model=User, time=updated_time):
        user.username = 'teste2'
        session.commit()

    session.refresh(user)

    assert user.username == 'teste2'
    assert user.created_at == initial_time
    assert user.updated_at == updated_time
