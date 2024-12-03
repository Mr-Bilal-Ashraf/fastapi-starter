from fastapi import APIRouter, BackgroundTasks, Depends, HTTPException, status
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session

from app.utils import account_activation_email
from app.serializers.user import UserCreate
from app.dependencies import get_session
from app.models.user import User

router = APIRouter()


@router.post("v1/users/create/")
async def create_new_user(
    user: UserCreate, bg_tasks: BackgroundTasks, db: Session = Depends(get_session)
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
