from sqlalchemy.orm import Session

from app.models.base import OTP

from random import randint


def generate_unique_token(db: Session):
    while True:
        code = randint(10000, 99999)
        if not db.query(OTP).filter(OTP.code == code).first():
            return code


def create_otp(db: Session, user_id: int, used_for: str):
    otp = generate_unique_token()
    obj = db.query(OTP).filter(OTP.user_id == user_id, OTP.used_for == used_for).first()
    if obj:
        db.delete(obj)
    obj = OTP(code=otp, used_for=used_for, user_id=user_id)
    db.add(obj)
    db.commit()
    return otp
