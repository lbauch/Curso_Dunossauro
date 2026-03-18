#!/bin/sh

# Aguarda 15 segundos, garantindo que o banco seja carregado
sleep 15
# Executa as migrações do banco de dados
poetry run alembic upgrade head

# Inicia a aplicação
poetry run uvicorn --host 0.0.0.0 --port 8000 curso_dunossauro.app:app