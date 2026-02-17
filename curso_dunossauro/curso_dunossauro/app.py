from http import HTTPStatus

from fastapi import FastAPI
from fastapi.responses import HTMLResponse

from curso_dunossauro.schemas import Message

app = FastAPI(title="Api curso Dunossauro", version="0.1.0")


@app.get("/", status_code=HTTPStatus.OK, response_model=Message)
def read_root():
    """
    Função olá mundo. Testando documentação
    """
    # return {"message": "Olá Mundo!"} - Também é possível enviar desta forma
    return Message(message="Olá Mundo!")


@app.get("/html", response_class=HTMLResponse)
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
