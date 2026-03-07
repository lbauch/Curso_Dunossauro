from http import HTTPStatus
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from curso_dunossauro.database import get_session
from curso_dunossauro.models import Todo, User
from curso_dunossauro.schemas import (
    FilterTodo,
    Message,
    TodoPublic,
    TodoSchema,
    TodoUpdate,
)
from curso_dunossauro.security import get_current_user

router = APIRouter(prefix='/todos', tags=['todos'])

T_Session = Annotated[AsyncSession, Depends(get_session)]
CurrentUser = Annotated[User, Depends(get_current_user)]


@router.post('/', response_model=TodoPublic)
async def create_todo(todo: TodoSchema, session: T_Session, user: CurrentUser):
    db_todo = Todo(
        # title=todo.title,
        # description=todo.description,
        # state=todo.state,
        user_id=user.id,
        **todo.model_dump(),
    )

    session.add(db_todo)
    await session.commit()
    await session.refresh(db_todo)

    return db_todo


@router.get('/', response_model=list[TodoPublic])
async def list_todos(
    session: T_Session,
    user: CurrentUser,
    todo_filter: Annotated[FilterTodo, Query()],
):
    query = select(Todo).where(Todo.user_id == user.id)

    if todo_filter.title:
        query = query.filter(Todo.title.contains(todo_filter.title))

    if todo_filter.description:
        query = query.filter(
            Todo.description.contains(todo_filter.description)
        )

    if todo_filter.state:
        query = query.filter(Todo.state == todo_filter.state)

    todos = await session.scalars(
        query.offset(todo_filter.offset).limit(todo_filter.limit)
    )

    return todos.all()


@router.patch('/{todo_id}', response_model=TodoPublic)
async def patch_todo(
    todo_id: int, session: T_Session, user: CurrentUser, todo: TodoUpdate
):
    db_todo = await session.scalar(
        select(Todo).where(Todo.user_id == user.id, Todo.id == todo_id)
    )

    if not db_todo:
        raise HTTPException(
            status_code=HTTPStatus.NOT_FOUND, detail='Task not found.'
        )

    for key, value in todo.model_dump(exclude_unset=True).items():
        setattr(db_todo, key, value)

    session.add(db_todo)
    await session.commit()
    await session.refresh(db_todo)

    return db_todo


@router.delete('/{todo_id}', response_model=Message)
async def delete_todo(todo_id: int, session: T_Session, user: CurrentUser):
    todo = await session.scalar(
        select(Todo).where(Todo.user_id == user.id, Todo.id == todo_id)
    )

    if not todo:
        raise HTTPException(
            status_code=HTTPStatus.NOT_FOUND, detail='Task not found.'
        )

    await session.delete(todo)

    return {'message': 'Task has been deleted successfully.'}
