from pydantic.dataclasses import dataclass
from pydantic import StrictInt

@dataclass
class Pessoa:
  name: str
  idade: int | None = 26 # Valida com casting - Interessante para api rest.
  ano_nasc: StrictInt | None = 2000 # Valida sem casting; Define o valor default caso não informado.


pessoa = Pessoa('teste')
print(pessoa)