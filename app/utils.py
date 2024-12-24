from fastapi import HTTPException, status, UploadFile

from sqlalchemy.orm import Session
from app.models.base import Base

from app.choices import OTPChoices
from app.models.user import User
from app.models.base import OTP
from app.config import settings

from random import randint
from pathlib import Path
from uuid import uuid4

from mailjet_rest import Client

PROFILE_PICTURE_DIR = Path("./app/static/profile_pictures/")
PROFILE_PICTURE_DIR.mkdir(parents=True, exist_ok=True)


def generate_unique_token(db: Session):
    while True:
        code = randint(10000, 99999)
        if not db.query(OTP).filter(OTP.code == code).first():
            return code


def create_otp(db: Session, user_id: int, used_for: str):
    otp = generate_unique_token(db)
    obj = db.query(OTP).filter(OTP.user_id == user_id, OTP.used_for == used_for).first()
    if obj:
        db.delete(obj)
    obj = OTP(code=otp, used_for=used_for, user_id=user_id)
    db.add(obj)
    db.commit()
    return otp


def send_email(to_email: str, subject: str, body: str):
    mailjet = Client(
        auth=(settings.MAILJET_API_PUB, settings.MAILJET_API_PRI), version="v3.1"
    )

    msg = {
        "Messages": [
            {
                "From": {
                    "Email": settings.MAILJET_SENDER_EMAIL,
                    "Name": settings.MAILJET_SENDER_NAME,
                },
                "To": [{"Email": to_email}],
                "Subject": subject,
                "TextPart": body,
                #   "HTMLPart": "<h3>Dear passenger 1, welcome to <a href=\"https://www.mailjet.com/\">Mailjet</a>!</h3><br />May the delivery force be with you!"
            }
        ]
    }

    resp = mailjet.send.create(data=msg)
    if resp.status_code == 200:
        print(f"\nemail sent to '{to_email}' successfully\n\n")
    else:
        print(f"\nemail sent to '{to_email}' failed\n\n")
        print(resp.json())


def account_activation_email(db: Session, user: User):
    otp = create_otp(db, user.id, OTPChoices.ACCOUNT_ACTIVATION)
    subject = "FastAPI Account Activation Token"
    name = f"{user.first_name}{' ' + user.last_name if user.last_name else ''}"
    body = f"Hi {name}, Your OTP for account activation is: {otp}. This OTP is valid for next 5 mins."
    return send_email(user.email, subject, body)


def email_forgot_password_token(db: Session, user: User):
    otp = create_otp(db, user.id, OTPChoices.FORGOT_PASSWORD)
    subject = "OTP to update your FastAPI Account password..."
    name = f"{user.first_name}{' ' + user.last_name if user.last_name else ''}"
    body = f"Hi {name}, Use this OTP: {otp} to update your password. This OTP is valid for next 2 mins."
    return send_email(user.email, subject, body)


def two_factor_token_email(db: Session, user: User):
    otp = create_otp(db, user.id, OTPChoices.TWO_FACTOR)
    subject = "Your FastAPI Two-Factor Authentication (2FA) Token..."
    name = f"{user.first_name}{' ' + user.last_name if user.last_name else ''}"
    body = f"Hi {name}, Use this OTP: {otp} to pass through Two-Factor Authentication (2FA). This OTP is valid for next 2 mins."
    return send_email(user.email, subject, body)


def update_email(db: Session, user: User, email: str):
    otp = create_otp(db, user.id, OTPChoices.UPDATE_EMAIL)
    subject = "Your FastAPI Update Email Token..."
    name = f"{user.first_name}{' ' + user.last_name if user.last_name else ''}"
    body = f"Hi {name}, Use this OTP: {otp} to update your email. This OTP is valid for next 2 mins."
    return send_email(email, subject, body)


def save_profile_picture(file: UploadFile) -> str:
    unique_filename = f"{uuid4().hex}_{file.filename}"
    file_location = PROFILE_PICTURE_DIR / unique_filename
    
    with open(file_location, "wb") as buffer:
        buffer.write(file.file.read())

    return str(file_location)


# ↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓ DB Utilities ↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓


def get_by_id(db: Session, model: Base, id: int):
    return db.query(model).filter(model.id == id).first()


def delete_by_id(db: Session, model: Base, id: int):
    obj = db.query(model).filter(model.id == id).first()
    if obj:
        db.delete(obj)
        db_commit(db)
        return True
    return False


def db_commit(db: Session):
    try:
        db.commit()
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed, due to internal server error, please try again later",
        )
