from http import HTTPStatus

from fastapi import FastAPI, HTTPException
from fastapi.responses import HTMLResponse

from curso_dunossauro.schemas import Message, UserDB, UserPublic, UserSchema

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
def create_user(user: UserSchema):
    # user_with_id = UserDB(   # - Formato HardCoding
    #     email="meu_email1@email.com",
    #     username="meu_user",
    #     password="psw1123",
    #     id=len(provisory_database) + 1
    # )
    # Melhor forma:
    user_with_id = UserDB(**user.model_dump(), id=len(provisory_database) + 1)
    provisory_database.append(user_with_id)
    return user_with_id


@app.get('/users', status_code=HTTPStatus.OK, response_model=list[UserPublic])
def read_users():
    return provisory_database


@app.get(
    '/users/{user_id}', status_code=HTTPStatus.OK, response_model=UserPublic
)
def read_user_by_id(user_id: int):
    if user_id < 1 or user_id > len(provisory_database):
        raise HTTPException(
            status_code=HTTPStatus.NOT_FOUND, detail='User Not Found'
        )
    return provisory_database[user_id - 1]


@app.put(
    '/users/{user_id}', status_code=HTTPStatus.OK, response_model=UserPublic
)
def update_user(user_id: int, user: UserSchema):
    if user_id < 1 or user_id > len(provisory_database):
        raise HTTPException(
            status_code=HTTPStatus.NOT_FOUND, detail='User Not Found'
        )
    user_with_id = UserDB(**user.model_dump(), id=user_id)
    provisory_database[user_id - 1] = user_with_id
    return user_with_id


@app.delete(
    '/users/{user_id}',
    status_code=HTTPStatus.OK,
    response_model=UserPublic,
)
def delete_user(user_id: int):
    if user_id < 1 or user_id > len(provisory_database):
        raise HTTPException(
            status_code=HTTPStatus.NOT_FOUND, detail='User Not Found'
        )
    return provisory_database.pop(user_id - 1)
