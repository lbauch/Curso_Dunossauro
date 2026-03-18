# from sqlalchemy import create_engine
# from sqlalchemy.orm import Session
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine

from curso_dunossauro.settings import Settings

engine = create_async_engine(Settings().DATABASE_URL)


# Ao utilizar o pragma_no_cover abaixo, indica para os testes que
# não é necessário cobrir esta parte.
# Isto ocorre por conta de a sessão ser sempre substituída nos testes
# afim de evitar conexões com o db real.
# Portanto, não se aplica aos testes.
async def get_session():  # pragma: no cover
    async with AsyncSession(
        engine,
        # abaixo evita que a sessão expire ao dar commit()
        expire_on_commit=False,
    ) as session:
        yield session
