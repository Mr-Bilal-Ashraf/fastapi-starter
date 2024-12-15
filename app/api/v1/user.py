from fastapi import APIRouter, BackgroundTasks, HTTPException, Security, status
from fastapi.responses import JSONResponse

from app.dependencies import JwtAuthDep, SessionDep, access_security, refresh_security
from app.serializers.user import (
    UserCreateSer,
    UserLoginSer,
    MyProfileSer,
    UserActivateSer,
)
from app.utils import account_activation_email, get_by_id, db_commit
from app.models.user import User
from app.models.base import OTP
from app.config import settings

from fastapi_jwt import JwtAuthorizationCredentials

from datetime import datetime, timezone, timedelta

router = APIRouter()


@router.post("/v1/users/create/")
async def create_new_user(
    db: SessionDep, user: UserCreateSer, bg_tasks: BackgroundTasks
):
    db_user = db.query(User).filter(User.email == user.email).first()
    if db_user:
        raise HTTPException(status_code=400, detail="Email already in use.")

    obj = User(**user.model_dump())
    obj.set_password(user.password)
    db.add(obj)
    db.commit()
    resp = {
        "id": obj.id,
        "email": obj.email,
        "msg": f"An Activation token is sent to {obj.email}.",
    }
    bg_tasks.add_task(account_activation_email, db, obj)
    return JSONResponse(content=resp, status_code=status.HTTP_201_CREATED)


@router.post("/v1/users/activate/")
async def activate_user_account(db: SessionDep, data: UserActivateSer):
    db_user = db.query(User).filter(User.email == data.email).first()
    if not db_user:
        raise HTTPException(status_code=404, detail="User not found.")
    if db_user.is_active:
        raise HTTPException(status_code=400, detail="User already active.")

    otp_result, otp_message = OTP.verify_otp(db, db_user, data.otp)
    if otp_result != 1:
        raise HTTPException(status_code=400, detail=otp_message)

    db_user.is_active = True
    db_commit(db)
    return {"detail": "User account successfully activated."}


@router.post("/v1/users/login/")
async def login(db: SessionDep, user: UserLoginSer, bg_tasks: BackgroundTasks):
    db_user = db.query(User).filter(User.email == user.email).first()
    if not db_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="No user matching the credentials.",
        )

    if not db_user.is_active:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="User is not active.",
        )

    if db_user.deleted:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="This account is deleted.",
        )

    if not db_user.verify_password(user.password):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid credentials.",
        )

    if db_user.two_factor:
        # bg_tasks.add_task(account_activation_email, db, db_user)  # Uncomment when 2FA is implemented
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="A two-factor OTP has been sent to your email.",
        )

    subject = {
        "id": db_user.id,
        "first_name": db_user.first_name,
        "last_name": db_user.last_name,
    }
    access_token = access_security.create_access_token(subject=subject)
    refresh_token = refresh_security.create_refresh_token(subject=subject)

    subject["is_superuser"] = db_user.is_superuser
    subject["email"] = db_user.email

    return {
        "access_token": access_token,
        "refresh_token": refresh_token,
        "user": subject,
    }


@router.post("/v1/users/refresh/token/")
def refresh_tokens(
    credentials: JwtAuthorizationCredentials = Security(refresh_security),
):
    access_token = access_security.create_access_token(subject=credentials.subject)
    refresh_token = refresh_security.create_refresh_token(
        subject=credentials.subject,
        expires_delta=timedelta(days=settings.REFRESH_TOKEN_EXPIRE),
    )

    return {"access_token": access_token, "refresh_token": refresh_token}


@router.post("/v1/users/resend_activation_token/")
async def resend_activation_token(
    db: SessionDep, email: str, bg_tasks: BackgroundTasks
):
    db_user = db.query(User).filter(User.email == email).first()
    if not db_user:
        raise HTTPException(status_code=404, detail="User not found.")
    if db_user.is_active:
        raise HTTPException(status_code=400, detail="User is already active.")
    bg_tasks.add_task(account_activation_email, db, db_user)
    return {"detail": "Activation token sent."}



@router.post("v1/users/delete/{pk}/", status_code=status.HTTP_204_NO_CONTENT)
async def delete_user(db: SessionDep, pk: int):
    db_user = get_by_id(db, User, pk)

@router.post("/v1/users/toggle_two_factor/", status_code=status.HTTP_200_OK)
async def toggle_two_factor(db: SessionDep, auth: JwtAuthDep):
    db_user: User = get_by_id(db, User, auth["id"])
    if not db_user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="User not found"
        )
    db_user.two_factor = not db_user.two_factor
    db_commit(db)
    return {"two_factor": db_user.two_factor}



@router.delete("/v1/users/me/", status_code=status.HTTP_204_NO_CONTENT)
async def delete_user(db: SessionDep, auth: JwtAuthDep):
    db_user: User = get_by_id(db, User, auth["id"])
    if not db_user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="User not found"
        )
    if db_user.deleted:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="User already deleted"
        )

    db_user.deleted_at = datetime.now(timezone.utc)
    db_user.is_active = False
    db_user.deleted = True
    db_commit(db)
    return None
