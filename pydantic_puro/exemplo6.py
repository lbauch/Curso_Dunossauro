import os
from dotenv import load_dotenv
from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import PostgresDsn

# Escolhe o ambiente
load_dotenv(".env")
ENV = os.getenv("ENV", "dev").lower()  # 'dev', 'prod', 'test'

class Settings(BaseSettings):
  postgres_url: PostgresDsn

  model_config = SettingsConfigDict(
    env_file=f".env.{ENV}",
    env_file_encoding="utf-8",
    env_prefix=f"{ENV}_"
  )

# Cria instância
settings = Settings()
print(settings.postgres_url)