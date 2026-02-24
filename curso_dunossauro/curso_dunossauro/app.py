from http import HTTPStatus

from fastapi import Depends, FastAPI, HTTPException
from fastapi.responses import HTMLResponse
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from curso_dunossauro.database import get_session
from curso_dunossauro.models import User
from curso_dunossauro.schemas import Message, UserPublic, UserSchema

app = FastAPI(title='Api curso Dunossauro', version='0.1.0')

provisory_database = []


@app.get('/', status_code=HTTPStatus.OK, response_model=Message)
def read_root():
    """
    Função olá mundo. Testando documentação
    """
    # return {"message": "Olá Mundo!"} - Também é possível enviar desta forma
    return Message(message='Olá Mundo!')


@app.get('/html', response_class=HTMLResponse)
def read_html():
    return """
    <html>
        <head>
            <title> Nosso olá mundo!</title>
        </head>
        <body>
            <h1> Olá Mundo </h1>
        </body>
    </html>"""


@app.post('/users', status_code=HTTPStatus.CREATED, response_model=UserPublic)
def create_user(user: UserSchema, session=Depends(get_session)):
    db_user = session.scalar(
        select(User).where(
            (User.username == user.username) | (User.email == user.email)
        )
    )
    if db_user:
        raise HTTPException(
            status_code=HTTPStatus.CONFLICT,
            detail='User with given email or username already exists.',
        )
    db_user = User(**user.model_dump())

    session.add(db_user)
    session.commit()
    session.refresh(db_user)

    return db_user


@app.get('/users', status_code=HTTPStatus.OK, response_model=list[UserPublic])
def read_users(
    limit: int = 10, offset: int = 0, session: Session = Depends(get_session)
):
    users = session.scalars(select(User).limit(limit).offset(offset))
    return users


@app.get(
    '/users/{user_id}', status_code=HTTPStatus.OK, response_model=UserPublic
)
def read_user_by_id(user_id: int, session: Session = Depends(get_session)):
    user_db = session.scalar(select(User).where(User.id == user_id))
    if not user_db:
        raise HTTPException(
            status_code=HTTPStatus.NOT_FOUND, detail='User Not Found'
        )
    return user_db


@app.put(
    '/users/{user_id}', status_code=HTTPStatus.OK, response_model=UserPublic
)
def update_user(
    user_id: int, user: UserSchema, session: Session = Depends(get_session)
):
    user_db = session.scalar(select(User).where(User.id == user_id))
    if not user_db:
        raise HTTPException(
            status_code=HTTPStatus.NOT_FOUND, detail='User Not Found'
        )

    # old_user = session.scalar(
    #     select(User).where(
    #         (User.username == user.username) | (User.email == user.email)
    #     )
    # )
    # if old_user:
    #     raise HTTPException(
    #         status_code=HTTPStatus.CONFLICT,
    #         detail='User with given email or username already exists.',
    #     )
    # Melhor Forma:

    try:
        user_db.email = user.email  # É possível fazer pelo model_dump()
        user_db.username = user.username  # É possível fazer pelo model_dump()
        user_db.password = user.password  # É possível fazer pelo model_dump()

        session.add(user_db)
        session.commit()
        session.refresh(user_db)  # Opicional

    except IntegrityError:
        raise HTTPException(
            status_code=HTTPStatus.CONFLICT,
            detail='User with given email or username already exists.',
        )

    return user_db


@app.delete(
    '/users/{user_id}',
    status_code=HTTPStatus.OK,
    response_model=Message,
)
def delete_user(user_id: int, session: Session = Depends(get_session)):
    user_db = session.scalar(select(User).where(User.id == user_id))
    if not user_db:
        raise HTTPException(
            status_code=HTTPStatus.NOT_FOUND, detail='User Not Found'
        )
    session.delete(user_db)
    session.commit()
    return {'message': 'User Deleted'}
