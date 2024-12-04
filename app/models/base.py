from sqlalchemy import Column, String, Integer, ForeignKey, DateTime
from sqlalchemy.orm import relationship, DeclarativeBase

from app.choices import OTPChoices

from datetime import datetime, timezone


class Base(DeclarativeBase):
    pass


class OTP(Base):
    __tablename__ = "otp"

    id = Column(Integer, primary_key=True)
    code = Column(String(10), nullable=False)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    user = relationship("User", back_populates="otps")
    used_for = Column(String(50), nullable=False, default=OTPChoices.ACCOUNT_ACTIVATION)
    s_time = Column(DateTime, default=datetime.now(timezone.utc), nullable=False)

    def __str__(self):
        return f"{self.user.name}, OTP for {self.used_for}"

    @classmethod
    def verify_otp(
        cls, session, user, code, v_type=OTPChoices.ACCOUNT_ACTIVATION, v_time=120
    ):
        try:
            # Fetch the last OTP for this user and type
            obj = (
                session.query(cls)
                .filter_by(user_id=user.id, used_for=v_type)
                .order_by(cls.s_time.desc())
                .first()
            )

            if obj:
                c_time = (datetime.utcnow() - obj.s_time).seconds <= v_time
                if c_time:
                    if code == obj.code:
                        return 1, ""  # OTP matched
                    else:
                        return 2, "OTP is Invalid."  # OTP Wrong
                return 3, "Your OTP got expired, try getting new one."  # Time Expired
            return 4, "OTP is Invalid/expired, try getting new one."  # No OTP found
        except Exception as e:
            print(f"\n\n{e}\n\n")
            return 4, "OTP is Invalid/expired, try getting new one."  # Error handling
