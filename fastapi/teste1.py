from fastapi import FastAPI, HTTPException, Depends
import uvicorn
from pydantic import Field#, BaseModel
from sqlmodel import Field, SQLModel, Session, create_engine, select
from contextlib import asynccontextmanager

# Pydantic class -+ SQLModel - serialization, validantion & DB
class BookBase(SQLModel):
  title: str = Field(index=True)
  author: str
  isbn: str = Field(min_length=4, max_length=5, default_factory='0011')
  description: str | None = None

class Book(BookBase, table=True):
  id: int | None = Field(primary_key=True)

# IMPORTANTE: Sem o uso de sqlmodel, seria necessário criar o modelo para serialização e validação
# e também criar a conexão com o database, conforme exemplo abaixo.
# Entretanto, o sqlmodel faz isto automaticamente, utilizando o modelo acima.

# # Serialization and validation
# class Book(BaseModel):
#   title: str
#   author: str
#   isbn: str
#   description: str

#   class Config:
#     orm_mode = True

# # database
# Base = declarative_base()
# class BookModel(Base):
#   __tablename__ = "books"
#   id = sqlalchemy.Column(sqlalchemy.Integer, primary_key=True, index=True)
#   title = sqlalchemy.Column(sqlalchemy.String, index=True)
#   author = sqlalchemy.Column(sqlalchemy.String, index=True)
#   description = sqlalchemy.Column(sqlalchemy.String, index=True)

sqlite_url = 'sqlite:///books.db'
connect_args = {'check_same_thread': False}
engine = create_engine(sqlite_url, echo=True, connect_args=connect_args)

def create_db_and_table():
  SQLModel.metadata.create_all(engine)

def get_session():
  with Session(engine) as session:
    yield(session)

@asynccontextmanager
async def lifespan(app: FastAPI):
  create_db_and_table()
  yield

app = FastAPI(lifespan=lifespan)

# Método antigo de inicialização
# @app.on_event('startup')
# def on_startup():
#   create_db_and_table()

@app.get('/')
def home_page():
  return {'title': 'Curso Teste'}

@app.post('/books')
def create_book(book: Book):
  with Session(engine) as session:
    db_item = book
    session.add(db_item)
    session.commit()
    session.refresh(db_item)
    return db_item

@app.get('/books', response_model=list[Book])
def read_books():
  with Session(engine) as session:
    books = session.exec(select(Book)).all()
    return books

# FAZENDO DA FORMA COMUM - NECESSÁRIO SEMPRE CRIAR A SEÇÃO
# @app.get('/books/{book_id}', response_model=Book)
# def read_book(book_id: int):
#   with Session(engine) as session:
#     book = session.get(Book, book_id)
#     if not book:
#       raise HTTPException(status_code=404, detail="Book Not Found")
#     return book


# Mesmo método que o acima comentado, porém, com dependência da sessão:
@app.get('/books/{book_id}', response_model=Book)
def read_book(book_id: int, session: Session = Depends(get_session)):
  book = session.get(Book, book_id)
  if not book:
    raise HTTPException(status_code=404, detail="Book Not Found")
  return book

@app.patch('/books/{book_id}', response_model=Book)
def update_book(book_id: int, book: Book, session: Session = Depends(get_session)):
  book_item = session.get(Book, book_id)
  if not book_item:
    raise HTTPException(status_code=404, detail="Book Not Found")
  book_data = book.model_dump(exclude_unset=True)
  for key, value in book_data.items():
    setattr(book_item, key, value)
  session.add(book_item)
  session.commit()
  session.refresh(book_item)
  return book_item

@app.delete('/books/{book_id}')
def delete_book(book_id: int, session: Session = Depends(get_session)):
  book = session.get(Book, book_id)
  if not book:
    raise HTTPException(status_code=404, detail="Book Not Found")
  session.delete(book)
  session.commit()
  return {'ok':True}

if __name__ == '__main__':
  uvicorn.run(app, host='127.0.0.1', port=7654)