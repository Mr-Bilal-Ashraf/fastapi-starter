from sqlalchemy import Column, Integer, String, Boolean, DateTime, Date
from sqlalchemy.orm import relationship
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
    deleted = Column(Boolean, default=False)
    deleted_at = Column(DateTime, nullable=True)
    two_factor = Column(Boolean, default=False)

    otps = relationship("OTP", back_populates="user")

    def __repr__(self):
        return f"<User(username={self.username}, email={self.email}, is_active={self.is_active})>"

    def verify_password(self, password: str) -> bool:
        return pwd_context.verify(password, self.password)

    def set_password(self, password: str):
        self.password = pwd_context.hash(password)
