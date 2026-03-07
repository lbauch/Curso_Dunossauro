from datetime import datetime
from enum import Enum

from sqlalchemy import ForeignKey, func
from sqlalchemy.orm import Mapped, mapped_column, registry, relationship

table_registry = registry()


@table_registry.mapped_as_dataclass
class User:
    __tablename__ = 'users'

    id: Mapped[int] = mapped_column(init=False, primary_key=True)
    username: Mapped[str] = mapped_column(unique=True)
    email: Mapped[str] = mapped_column(unique=True)
    password: Mapped[str]
    created_at: Mapped[datetime] = mapped_column(
        init=False, server_default=func.now()
    )
    updated_at: Mapped[datetime] = mapped_column(
        init=False, server_default=func.now(), onupdate=func.now()
    )
    todos: Mapped[list['Todo']] = relationship(
        init=False,
        # TODOS, os todos de um determinado user sejam deletados
        # ao deletar o user
        cascade='all, delete-orphan',
        lazy='selectin',
    )


class TodoState(str, Enum):
    DRAFT = 'draft'
    TODO = 'todo'
    DOING = 'doing'
    DONE = 'done'
    THRASH = 'thrash'


# from enum import IntEnum
# class TodoState(IntEnum):
#     draft = 1
#     todo = 2
#     doing = 3
#     done = 4
#     trash = 5


@table_registry.mapped_as_dataclass
class Todo:
    __tablename__ = 'todos'

    id: Mapped[int] = mapped_column(init=False, primary_key=True)
    title: Mapped[str]
    description: Mapped[str]
    state: Mapped[TodoState]

    user_id: Mapped[int] = mapped_column(ForeignKey('users.id'))
