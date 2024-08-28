from datetime import timedelta
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from jose import JWTError
from sqlalchemy.orm import Session

import app.models as models
from app.core.config import settings
from app.core.security import (
    blacklist_token,
    create_access_token,
    get_password_hash,
    is_blacklisted,
    oauth2_scheme,
)
from app.db.database import get_db
from app.schemas import schemas

from ..dependencies import authenticate_user, user_already_registered

router: APIRouter = APIRouter(prefix="/auth", tags=["Auth"])


@router.post(
    "/register",
    status_code=status.HTTP_201_CREATED,
    response_description="Registration confirmation",
)
async def register_new_user(
    user: schemas.UserCreate, db: Annotated[Session, Depends(get_db)]
) -> schemas.RegisterResponse:
    """
    Register a new user.
    """

    hashed_password = get_password_hash(user.password.get_secret_value())
    new_user = models.UserORM(
        username=user.username,
        email=user.email,
        hashed_password=hashed_password,
    )

    if user_already_registered(new_user, db):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Client already registered.",
        )

    try:
        db.add(new_user)
        db.commit()
        db.refresh(new_user)
        message = f"User {new_user.username} registered successfully."
        return schemas.RegisterResponse(
            status=schemas.Status.Success, message=message
        )
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An error occurred while registering the user.",
        ) from e


@router.post(
    "/login",
    response_description="Access token",
)
async def login(
    form_data: Annotated[OAuth2PasswordRequestForm, Depends()],
    db: Annotated[Session, Depends(get_db)],
) -> schemas.Token:
    user = authenticate_user(form_data.username, form_data.password, db)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    access_token_expires = timedelta(
        minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES
    )
    access_token = create_access_token(
        data={"sub": user.username}, expires_delta=access_token_expires
    )
    return schemas.Token(
        access_token=access_token, token_type="bearer"
    )  # nosec


@router.post(
    "/logout",
    response_description="Logout confirmation",
)
async def logout(
    access_token: Annotated[str, Depends(oauth2_scheme)],
    db: Annotated[Session, Depends(get_db)],
) -> dict[str, str]:
    unauthorized_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Invalid token.",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        if is_blacklisted(access_token, db):
            raise unauthorized_exception
        blacklist_token(access_token, db)
    except JWTError:
        unauthorized_exception
    return {"message": "Logged out successfully"}
