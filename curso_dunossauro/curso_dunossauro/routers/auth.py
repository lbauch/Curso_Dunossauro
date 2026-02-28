from http import HTTPStatus
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from curso_dunossauro.database import get_session
from curso_dunossauro.models import User
from curso_dunossauro.schemas import Token
from curso_dunossauro.security import create_access_token, verify_password

router = APIRouter(prefix='/auth', tags=['auth'])
# Variáveis de tipos são utilizadas com CamelCase. Utiliza-se:
# T_TipoDaVariavelOriginal - Boa prática: https://peps.python.org/pep-0008/#type-variable-names
T_Session = Annotated[AsyncSession, Depends(get_session)]
OAuthForm = Annotated[OAuth2PasswordRequestForm, Depends()]


@router.post('/token', response_model=Token)
async def login_for_access_token(session: T_Session, form_data: OAuthForm):
    # Neste caso, o email será utilizado como campo de validação único.
    user = await session.scalar(
        select(User).where(User.email == form_data.username)
    )

    if not user:
        raise HTTPException(
            status_code=HTTPStatus.UNAUTHORIZED,
            detail='Incorrect email or password',
        )

    if not verify_password(form_data.password, user.password):
        raise HTTPException(
            status_code=HTTPStatus.UNAUTHORIZED,
            detail='Incorrect email or password',
        )

    access_token = create_access_token(data={'sub': user.email})

    return {'access_token': access_token, 'token_type': 'bearer'}
