from pydantic import BaseModel, field_validator, model_validator
from typing_extensions import Self

class Cadastro(BaseModel):
  email: str
  senha_1: str
  senha_2: str

  @field_validator('email')
  def email_com_arroba(cls, v):
    if not '@' in v:
      raise ValueError('Sem @')
    return v # Necessário retornar o próprio valor. Caso contrário, fica nulo

  # @field_validator('*') --- Valida todos os campos
  @field_validator('senha_1', 'senha_2')
  def senha_segura(cls, v):
    if len(v) < 3:
      raise ValueError('Senha Pequena')
    return v
    
  @model_validator(mode='after')
  def check_passwords_match(self) -> Self:
      if self.senha_1 != self.senha_2:
        raise ValueError('Passwords do not match')
      return self

cad_1 = {'email': '123@gmail', 'senha_1': '1234', 'senha_2': '1234'}

# cad_2 = {'email': 'gmail', 'senha_1': '1234', 'senha_2': '1234'}
# cad_2 = {'email': 'gmail', 'senha_1': '1', 'senha_2': '45'}
# cad_2 = {'email': 'gmail@', 'senha_1': '1234', 'senha_2': '1'}
cad_2 = {'email': 'gmail@', 'senha_1': '1234', 'senha_2': '4321'}

cadastro_1 = Cadastro(**cad_1)
print(f'cadastro_1: {cadastro_1}')
cadastro_2 = Cadastro(**cad_2)
print(f'cadastro_2: {cadastro_2}')