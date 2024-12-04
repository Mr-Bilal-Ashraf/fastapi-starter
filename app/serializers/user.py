from pydantic import BaseModel, Field

from datetime import datetime


class UserResponseSer(BaseModel):
    id: int
    # username: str
    email: str
    first_name: str
    last_name: str
    date_of_birth: str = None
    profile_picture: str = None
    last_login: datetime = None
    is_active: bool
    is_superuser: bool
    date_joined: datetime

    class Config:
        orm_mode = True


class UserCreateSer(BaseModel):
    # username: str = Field(min_length=1, max_length=50)
    email: str = Field(min_length=15, max_length=70)
    password: str = Field(min_length=8, max_length=50)
    first_name: str = Field(min_length=5, max_length=150)
    last_name: str | None = Field(min_length=5, max_length=150)


class UserLoginSer(BaseModel):
    email: str = Field(min_length=15, max_length=70)
    password: str = Field(min_length=8, max_length=50)
