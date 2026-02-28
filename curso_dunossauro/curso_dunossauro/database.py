# from sqlalchemy import create_engine
# from sqlalchemy.orm import Session
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine

from curso_dunossauro.settings import Settings

engine = create_async_engine(Settings().DATABASE_URL)


async def get_session():
    async with AsyncSession(
        engine,
        # abaixo evita que a sessão expire ao dar commit()
        expire_on_commit=False,
    ) as session:
        yield session
