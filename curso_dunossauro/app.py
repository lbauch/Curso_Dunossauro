import asyncio
import sys
from http import HTTPStatus

from fastapi import FastAPI

from curso_dunossauro.schemas import Message

from .routers import auth_router, todos_router, users_router

if sys.platform == 'win32':
    asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())

app = FastAPI(title='Api curso Dunossauro', version='0.1.0')

app.include_router(auth_router)
app.include_router(users_router)
app.include_router(todos_router)


@app.get('/', status_code=HTTPStatus.OK, response_model=Message)
def read_root():
    return Message(message='Olá Mundo!')
