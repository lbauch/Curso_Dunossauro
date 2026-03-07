from http import HTTPStatus

import factory
import factory.fuzzy
import pytest
from sqlalchemy import select

from curso_dunossauro.models import Todo, TodoState


class TodoFactory(factory.Factory):
    class Meta:
        model = Todo

    title = factory.Faker('text')  # Cria texto aleatório
    description = factory.Faker('text')
    state = factory.fuzzy.FuzzyChoice(TodoState)  # Escolhe estado aleatório
    user_id = 1


def test_create_todo(client, token, mock_db_time):
    with mock_db_time(model=Todo) as time:
        response = client.post(
            '/todos/',
            headers={'Authorization': f'Bearer {token}'},
            json={
                'title': 'Test Todo',
                'description': 'Test todo description',
                'state': 'draft',
            },
        )
        assert response.json() == {
            'id': 1,
            'title': 'Test Todo',
            'description': 'Test todo description',
            'state': 'draft',
            'created_at': time.isoformat(),
            'updated_at': time.isoformat(),
        }


@pytest.mark.asyncio
async def test_list_todos_should_return_5_todos(session, client, user, token):
    expected_todos = 5
    session.add_all(TodoFactory.create_batch(expected_todos, user_id=user.id))
    await session.commit()

    response = client.get(
        '/todos/',
        headers={'Authorization': f'Bearer {token}'},
    )

    # assert len(response.json()['todos']) == expected_todos
    assert len(response.json()) == expected_todos


@pytest.mark.asyncio
async def test_list_todos_pagination_should_return_2_todos(
    session, user, client, token
):
    expected_todos = 2
    session.add_all(TodoFactory.create_batch(5, user_id=user.id))
    await session.commit()

    response = client.get(
        '/todos/?offset=1&limit=2',
        headers={'Authorization': f'Bearer {token}'},
    )

    assert len(response.json()) == expected_todos


@pytest.mark.asyncio
async def test_list_todos_filter_title_should_return_5_todos(
    session, user, client, token
):
    expected_todos = 5
    session.add_all(
        TodoFactory.create_batch(5, user_id=user.id, title='Test todo 1')
    )
    session.add_all(TodoFactory.create_batch(5, user_id=user.id))
    await session.commit()

    response = client.get(
        '/todos/?title=Test todo 1',
        headers={'Authorization': f'Bearer {token}'},
    )

    assert len(response.json()) == expected_todos


@pytest.mark.asyncio
async def test_list_todos_filter_description_should_return_5_todos(
    session, user, client, token
):
    expected_todos = 5
    session.add_all(
        TodoFactory.create_batch(
            5, user_id=user.id, description='Test desc todo 1'
        )
    )
    session.add_all(TodoFactory.create_batch(5, user_id=user.id))
    await session.commit()

    response = client.get(
        # Procurar somente um pedaço da description
        '/todos/?description=Test desc',
        headers={'Authorization': f'Bearer {token}'},
    )

    assert len(response.json()) == expected_todos


@pytest.mark.asyncio
async def test_list_todos_filter_state_should_return_5_todos(
    session, user, client, token
):
    expected_todos = 5
    session.add_all(
        TodoFactory.create_batch(5, user_id=user.id, state=TodoState.DRAFT)
    )
    session.add_all(
        TodoFactory.create_batch(5, user_id=user.id, state=TodoState.DOING)
    )
    await session.commit()

    response = client.get(
        # Procurar somente um pedaço da description
        '/todos/?state=draft',
        headers={'Authorization': f'Bearer {token}'},
    )

    assert len(response.json()) == expected_todos


@pytest.mark.asyncio
async def test_list_todos_filter_combined(session, user, client, token):
    expected_todos = 5
    filter_default = 10
    session.add_all(
        TodoFactory.create_batch(
            expected_todos,
            user_id=user.id,
            title='Meu Title Novo padrão',
            state=TodoState.DOING,
        )
    )
    session.add_all(
        TodoFactory.create_batch(
            expected_todos,
            user_id=user.id,
            title='Meu Title Novo padrão',
            description='Minha desc 1',
            state=TodoState.DOING,
        )
    )
    session.add_all(
        TodoFactory.create_batch(
            expected_todos,
            user_id=user.id,
            title='Meu Title Novo padrão',
            description='Minha desc 1',
            state=TodoState.DRAFT,
        )
    )
    await session.commit()

    response_full = client.get(
        '/todos/?title=Meu%20Title&description=Minha%20desc&state=draft',
        headers={'Authorization': f'Bearer {token}'},
    )

    response_description = client.get(
        '/todos/?title=Meu%20Title&description=Minha%20desc%20',
        headers={'Authorization': f'Bearer {token}'},
    )

    response_title_partial = client.get(
        '/todos/?title=Meu%20Title',
        headers={'Authorization': f'Bearer {token}'},
    )

    response_title_full = client.get(
        # Procurar somente um pedaço da description
        '/todos/?title=Meu%20Title&limit=15',
        headers={'Authorization': f'Bearer {token}'},
    )

    assert len(response_full.json()) == expected_todos
    assert len(response_description.json()) == expected_todos * 2
    # filter padrão é 10.
    assert len(response_title_partial.json()) == filter_default
    assert len(response_title_full.json()) == expected_todos * 3


def test_patch_todo_error(client, token):
    response = client.patch(
        '/todos/10',
        json={},
        headers={'Authorization': f'Bearer {token}'},
    )
    assert response.status_code == HTTPStatus.NOT_FOUND
    assert response.json() == {'detail': 'Task not found.'}


@pytest.mark.asyncio
async def test_patch_todo(session, client, user, token):
    todo = TodoFactory(user_id=user.id)

    session.add(todo)
    await session.commit()

    response = client.patch(
        f'/todos/{todo.id}',
        json={'title': 'teste!'},
        headers={'Authorization': f'Bearer {token}'},
    )
    assert response.status_code == HTTPStatus.OK
    assert response.json()['title'] == 'teste!'


def test_delete_todo_error(client, token):
    response = client.delete(
        f'/todos/{10}', headers={'Authorization': f'Bearer {token}'}
    )

    assert response.status_code == HTTPStatus.NOT_FOUND
    assert response.json() == {'detail': 'Task not found.'}


@pytest.mark.asyncio
async def test_delete_todo(session, client, user, token):
    todo = TodoFactory(user_id=user.id)

    session.add(todo)
    await session.commit()

    response = client.delete(
        f'/todos/{todo.id}', headers={'Authorization': f'Bearer {token}'}
    )

    assert response.status_code == HTTPStatus.OK
    assert response.json() == {
        'message': 'Task has been deleted successfully.'
    }


@pytest.mark.asyncio
async def test_delete_ohter_user_todo(session, client, other_user, token):
    todo_other_user = TodoFactory(user_id=other_user.id)

    session.add(todo_other_user)
    await session.commit()

    response = client.delete(
        f'/todos/{todo_other_user.id}',
        headers={'Authorization': f'Bearer {token}'},
    )

    assert response.status_code == HTTPStatus.NOT_FOUND
    assert response.json() == {'detail': 'Task not found.'}


@pytest.mark.asyncio
async def test_list_todos_should_return_all_expected_fields__exercicio(
    session, client, user, token, mock_db_time
):
    with mock_db_time(model=Todo) as time:
        todo = TodoFactory.create(user_id=user.id)
        session.add(todo)
        await session.commit()

    await session.refresh(todo)
    response = client.get(
        '/todos/',
        headers={'Authorization': f'Bearer {token}'},
    )

    assert response.json() == [
        {
            'created_at': time.isoformat(),
            'updated_at': time.isoformat(),
            'description': todo.description,
            'id': todo.id,
            'state': todo.state,
            'title': todo.title,
        }
    ]


@pytest.mark.asyncio
async def test_create_todo_error(session, user):
    todo = Todo(
        title='Test Todo',
        description='Test Desc',
        state='test',
        user_id=user.id,
    )

    session.add(todo)
    await session.commit()

    with pytest.raises(LookupError):
        await session.scalar(select(Todo))
