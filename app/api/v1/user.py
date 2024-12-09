from fastapi import APIRouter, BackgroundTasks, HTTPException, Security, status
from fastapi.responses import JSONResponse

from app.dependencies import JwtAuthDep, SessionDep, access_security, refresh_security
from app.serializers.user import UserCreateSer, UserLoginSer, MyProfileSer
from app.utils import account_activation_email, get_by_id
from app.models.user import User
from app.config import settings

from fastapi_jwt import JwtAuthorizationCredentials

from datetime import timedelta

router = APIRouter()


@router.post("v1/users/create/")
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


async def activate_user_account(db: SessionDep, user_id: int):
@router.post("v1/users/login/")
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

    return JSONResponse(
        content={
            "access_token": access_token,
            "refresh_token": refresh_token,
            "user": subject,
        },
        status_code=status.HTTP_200_OK,
    )

@router.post("v1/users/refresh")
def refresh_tokens(credentials: JwtAuthorizationCredentials = Security(refresh_security)):
    access_token = access_security.create_access_token(subject=credentials.subject)
    refresh_token = refresh_security.create_refresh_token(
        subject=credentials.subject,
        expires_delta=timedelta(days=settings.REFRESH_TOKEN_EXPIRE)
    )

    return JSONResponse(
        content={
            "access_token": access_token,
            "refresh_token": refresh_token
        },
        status_code=status.HTTP_200_OK,
    )



@router.post("v1/users/delete/{pk}/", status_code=status.HTTP_204_NO_CONTENT)
async def delete_user(db: SessionDep, pk: int):
    db_user = get_by_id(db, User, pk)
async def delete_user(db: SessionDep, auth: JwtAuthDep):
    db_user = get_by_id(db, User, auth["id"])
    if not db_user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="User not found"
        )
    if db_user.deleted:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="User already deleted"
        )

    db_user.deleted = True
    db.commit()
    return None
