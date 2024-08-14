import bcrypt
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

import app.models as models
from app.database import get_db
from app.schemas import schemas

router: APIRouter = APIRouter()


@router.post(
    "/register/",
    status_code=status.HTTP_201_CREATED,
    response_model=schemas.RegisterResponse,
)
def register_user(user: schemas.UserCreate, db: Session = Depends(get_db)):
    try:
        hashed_password = bcrypt.hashpw(
            user.password.encode(), bcrypt.gensalt()
        ).decode()
        new_user = models.UserORM(
            username=user.username,
            email=user.email,
            hashed_password=hashed_password,
        )
        db.add(new_user)
        db.commit()
        db.refresh(new_user)
        message = f"User {new_user.username} registered successfully."
        return schemas.RegisterResponse(
            status=schemas.Status.Success, message=message
        )
    except Exception:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An error occurred while registering the user.",
        )
