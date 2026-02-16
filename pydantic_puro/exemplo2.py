from pydantic import BaseModel

class Pessoa(BaseModel):
  nome: str
  idade: int

class Kid(Pessoa):
  responsavel: str

class Adulto(Pessoa): # Fazer desta forma, herda todos os campos de pessoa.
  parceiro: str

class Funcionario(BaseModel):
  pessoa: Pessoa

class Festa(BaseModel):
  pessoas_errado: list[Pessoa]  # Espera valores de Pesso. Portanto, irá desconsiderar o campo parceiro.
  maiores: list[Adulto]
  menores: list[Kid]
  responsavel: Funcionario

maiores = [
  {'nome':'João', 'idade':25, 'parceiro':'Maria'},
  {'nome':'Pedro', 'idade':27, 'parceiro':'Joana'}
]

menores = [
  {'nome':'José', 'idade':13, 'responsavel': 'Márcio'},
  {'nome':'Antony', 'idade':11, 'responsavel': 'Josue'}
]

funcionario = {'pessoa':{'nome':'Jacson', 'idade':39}}

festa = {
  'pessoas_errado': maiores, # Espera valores de Pesso. Portanto, desconsidera o campo parceiro.
  'maiores': maiores,
  'menores': menores,
  'responsavel': funcionario,
  'item_errado': 'desconsiderado' # Não está no modelo, logo, não é passado adiante.
}

festa_dump = Festa(**festa)
print(festa_dump)