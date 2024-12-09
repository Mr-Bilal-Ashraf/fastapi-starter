from fastapi import Depends

from sqlalchemy.orm import Session
from sqlalchemy import create_engine

from app.config import settings

from fastapi_jwt import JwtAccessBearerCookie, JwtRefreshBearer

from datetime import timedelta
from typing import Annotated


engine = create_engine(settings.DATABASE_URL, connect_args={"check_same_thread": False})


def get_session():
    with Session(engine) as session:
        yield session


access_security = JwtAccessBearerCookie(
    secret_key=settings.SECRET_KEY,
    auto_error=False,
    access_expires_delta=timedelta(hours=settings.ACCESS_TOKEN_EXPIRE),
)
refresh_security = JwtRefreshBearer(
    secret_key=settings.SECRET_KEY,
    auto_error=True,
    refresh_expires_delta=timedelta(days=settings.REFRESH_TOKEN_EXPIRE),
)

SessionDep = Annotated[Session, Depends(get_session)]
