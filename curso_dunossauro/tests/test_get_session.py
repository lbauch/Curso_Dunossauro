# import pytest
# from sqlalchemy.ext.asyncio import create_async_engine

# from curso_dunossauro import database

# Este teste torna-se desnecessário por conta do trecho
#   # pragma: no cover no arquivo de database

# @pytest.mark.asyncio
# async def test_get_session_generator(monkeypatch):
#     """
#     Função para testar o banco em memória.
#     Sobrescreve a engine padrão e testa obter sessão
#     Forja um banco em memória para evitar conexão com produção.
#     Função em arquivo separado para não importar o database em outros testes.
#     """
#     test_engine = create_async_engine('sqlite+aiosqlite:///:memory:')
#     # Sobrescreve a engine padrão. - MUITO IMPORTANTE
#     monkeypatch.setattr(database, 'engine', test_engine)

#     async for session in database.get_session():
#         engine_url = str(session.get_bind().url)
#         assert session is not None
#         assert session.is_active
#         assert engine_url == 'sqlite+aiosqlite:///:memory:'
