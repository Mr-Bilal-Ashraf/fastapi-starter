from fastapi import Depends

from sqlalchemy.orm import Session
from sqlalchemy import create_engine

from typing import Annotated

from app.config import settings


engine = create_engine(settings.DATABASE_URL, connect_args={"check_same_thread": False})


def get_session():
    with Session(engine) as session:
        yield session


SessionDep = Annotated[Session, Depends(get_session)]
