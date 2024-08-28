from typing import Annotated, Any

from fastapi import Depends, HTTPException, status
from sqlalchemy.orm import Session

import app.models as models
from app.core.security import oauth2_scheme, verify_password, verify_token
from app.db.database import get_db


def get_user(username: str | None, db: Session) -> Any:
    return (
        db.query(models.UserORM)
        .filter(models.UserORM.username == username)
        .first()
    )


def user_already_registered(user: models.UserORM, db: Session) -> bool:
    return (
        db.query(models.UserORM)
        .filter(
            models.UserORM.username == user.username
            or models.UserORM.email == user.email
        )
        .first()
        is not None
    )


def authenticate_user(
    username: str, password: str, db: Session
) -> models.UserORM | None:
    user = get_user(username, db)
    if not user:
        return None
    return user if verify_password(password, user.hashed_password) else None


def get_current_user(
    token: Annotated[str, Depends(oauth2_scheme)],
    db: Annotated[Session, Depends(get_db)],
):
    token_data = verify_token(token, db)
    user = get_user(token_data.username, db)

    if user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )

    return user


async def get_current_active_user(
    current_user: Annotated[models.UserORM, Depends(get_current_user)],
):
    if not current_user.is_active:
        raise HTTPException(status_code=400, detail="Inactive user")
    return current_user
