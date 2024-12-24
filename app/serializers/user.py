from pydantic import BaseModel, Field, EmailStr

from datetime import date, datetime


class UserResponseSer(BaseModel):
    id: int
    # username: str
    email: EmailStr
    first_name: str
    last_name: str
    date_of_birth: date | None 
    profile_picture: str | None
    last_login: datetime | None
    is_active: bool
    is_superuser: bool
    date_joined: datetime

    class Config:
        from_attributes = True


class UserCreateSer(BaseModel):
    # username: str = Field(min_length=1, max_length=50)
    email: EmailStr = Field(min_length=15, max_length=70)
    password: str = Field(min_length=8, max_length=50)
    first_name: str = Field(min_length=5, max_length=150)
    last_name: str | None = Field(min_length=5, max_length=150)


class UserLoginSer(BaseModel):
    email: EmailStr = Field(min_length=15, max_length=70)
    password: str = Field(min_length=8, max_length=50)


class UserActivateSer(BaseModel):
    email: EmailStr = Field(min_length=15, max_length=70)
    otp: str | int


class UserForgotPasswordSer(UserActivateSer):
    password: str = Field(min_length=8, max_length=50)


class ValidateTwoFactorSer(UserActivateSer):
    pass


class UpdateEmailSer(BaseModel):
    email: EmailStr = Field(min_length=15, max_length=70)
    otp: str | int | None = None
