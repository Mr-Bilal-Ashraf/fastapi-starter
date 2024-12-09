from fastapi import APIRouter, BackgroundTasks, Depends, HTTPException, status
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session

from app.dependencies import SessionDep, access_security, refresh_security
from app.serializers.user import UserCreateSer, UserLoginSer, MyProfileSer
from app.utils import account_activation_email, get_by_id
from app.models.user import User

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
        # bg_tasks.add_task(account_activation_email, db, db_user)
        return JSONResponse(
            content={
                "two_factor": True,
                "user": db_user.id,
                "message": "A two factor OTP is sent to your mail."
            },
            status_code=status.HTTP_400_BAD_REQUEST,
        # bg_tasks.add_task(account_activation_email, db, db_user)  # Uncomment when 2FA is implemented
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="A two-factor OTP has been sent to your email.",
        )

        )
