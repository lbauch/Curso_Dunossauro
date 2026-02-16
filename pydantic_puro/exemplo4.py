from pydantic import BaseModel, Field, EmailStr
from datetime import datetime

class User(BaseModel):
  email: EmailStr # Valida automaticamente se o campo enviado é um email.
  username: str = Field(default_factory=lambda data: data['email'])


class MyClass(BaseModel):
  # nr maior que 0 e menor ou igual a 10. 
  numero: int = Field(1, le=10, gt=0, alias='nr')
  # Lista com no máximo 3 itens
  lista: list[int] = Field([], max_length=3)
  criado_em: datetime = Field(default_factory=datetime.now)


classe = MyClass(nr=10)
print(classe.model_dump(by_alias=True))
print(classe)

user = User(email='user@example.com')
print(user.email)
print(user.username)

user2 = User(email='userexample.com')
# user = User(email='user@example')
print(user2.username)
