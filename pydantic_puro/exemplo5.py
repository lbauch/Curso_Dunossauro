from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import PostgresDsn

class DevSettings(BaseSettings):
  # postgres://user:pass@localhost:5432/foobar
  # representa: postgres://usuario:senha@host:porta/nome_do_banco
  postgres_url: PostgresDsn # pydantic compara o nome_da_variavel e localiza NOME_DA_VARIAVEL no .env

  model_config = SettingsConfigDict(
    env_file='.env',
    env_file_encoding='utf-8',
    env_prefix='dev_',
    # extra='forbid' - valor default é forbid. Caso queira permitir e ignorar, utilizar 
  )

settings = DevSettings()
print(settings.postgres_url)

# Exemplo de conexão com o banco:
# engine = create_engine(str(settings.postgres_url))

# with engine.connect() as connection:
#     result = connection.execute("SELECT 1")
#     print(result.scalar())