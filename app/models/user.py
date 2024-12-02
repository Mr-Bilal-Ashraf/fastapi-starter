from sqlalchemy import Column, Integer, String, Boolean, DateTime, Date
from passlib.context import CryptContext
from datetime import datetime, timezone

from app.models.base import Base

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    # username = Column(String(50), unique=True, index=True)
    email = Column(String(70), unique=True, index=True)
    first_name = Column(String(150))
    last_name = Column(String(150), nullable=True)
    date_of_birth = Column(Date, nullable=True)
    password = Column(String(128), nullable=False)
    profile_picture = Column(String(255), nullable=True)
    last_login = Column(DateTime, nullable=True)
    is_active = Column(Boolean, default=False)
    is_superuser = Column(Boolean, default=False)
    date_joined = Column(DateTime, default=datetime.now(timezone.utc))

    def __repr__(self):
        return f"<User(username={self.username}, email={self.email}, is_active={self.is_active})>"

    def verify_password(self, password: str) -> bool:
        return pwd_context.verify(password, self.password)

    def set_password(self, password: str):
        self.password = pwd_context.hash(password)


# # Example SQLAlchemy Manager / Helper Methods
# def create_user(db_session, username: str, email: str, password: str, **kwargs):
#     user = User(username=username, email=email, **kwargs)
#     user.set_password(password)
#     db_session.add(user)
#     db_session.commit()
#     db_session.refresh(user)
#     return user


# def create_superuser(db_session, username: str, email: str, password: str, **kwargs):
#     user = create_user(db_session, username, email, password, **kwargs)
#     user.is_staff = True
#     user.is_superuser = True
#     db_session.commit()
#     return user


# #  *****************************************************************


# from fastapi import FastAPI, Depends, HTTPException
# from sqlalchemy import create_engine
# from sqlalchemy.orm import sessionmaker
# from sqlalchemy.orm import Session
# from pydantic import BaseModel
# from typing import List
# from datetime import datetime


# # def get_user_by_id(db: Session, user_id: int):
# #     return db.query(User).filter(User.id == user_id).first()


# # @app.get("/users/{user_id}", response_model=UserOut)
# # def read_user(user_id: int, db: Session = Depends(get_db)):
# #     db_user = get_user_by_id(db, user_id)
# #     if db_user is None:
# #         raise HTTPException(status_code=404, detail="User not found")
# #     return db_user


# #  *****************************************************************************
