from fastapi import FastAPI

app = FastAPI()


@app.get("/")
def read_root():
    """
    Função olá mundo. Testando documentação
    """
    return {"message": "Olá Mundo!"}
