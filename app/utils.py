from sqlalchemy.orm import Session
from app.models.base import Base

from app.choices import OTPChoices
from app.models.user import User
from app.models.base import OTP
from app.config import settings

from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from random import randint

import smtplib


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
    """
    Following error have to be fixed:

    Error sending email: (535, b'5.7.8 Username and Password not accepted. 
    For more information, go to\n5.7.8  https://support.google.com/mail/?p=BadCredentials 4fb4d7f45d1cf-5d097db0a6esm5835969a12.27 - gsmtp')
    """
    msg = MIMEMultipart()
    msg['From'] = settings.FROM_EMAIL
    msg['To'] = to_email
    msg['Subject'] = subject

    msg.attach(MIMEText(body, 'plain'))

    try:
        with smtplib.SMTP_SSL(settings.SMTP_SERVER, settings.SMTP_PORT) as server:
            server.login(settings.SMTP_USER, settings.SMTP_PASSWORD)
            server.sendmail(settings.FROM_EMAIL, to_email, msg.as_string())
    except Exception as e:
        print(f"Error sending email: {e}")
        return False
    return True


def account_activation_email(db: Session, user: User):
    otp = create_otp(db, user.id, OTPChoices.ACCOUNT_ACTIVATION)
    subject = "FastAPI Account Activation Token"
    name = f"{user.first_name}{' ' + user.last_name if user.last_name else ''}"
    body = f"Hi {name}, Your OTP for account activation is: {otp}"
    return send_email(user.email, subject, body)


def get_by_id(db: Session, model: Base, id: int):
    return db.query(model).filter(model.id == id).first()
