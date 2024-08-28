from typing import Annotated, Literal

import jwt
from fastapi import Depends, HTTPException, status
from jwt.exceptions import ExpiredSignatureError, InvalidTokenError
from sqlalchemy.orm import Session

import app.models as models
from app.core.config import settings
from app.core.security import is_blacklisted, oauth2_scheme, verify_password
from app.db.database import get_db
from app.schemas import schemas


def get_user(username: str | None, db: Session) -> models.UserORM | None:
    if username is None:
        return None

    user = (
        db.query(models.UserORM)
        .filter(models.UserORM.username == username)
        .first()
    )

    return user or None


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
) -> models.UserORM | Literal[False]:
    user = get_user(username, db)
    if not user:
        return False
    elif not verify_password(password, user.hashed_password):
        return False
    return user


def get_current_user(
    token: Annotated[str, Depends(oauth2_scheme)],
    db: Annotated[Session, Depends(get_db)],
):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )

    if is_blacklisted(token, db):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token has been blacklisted, please log in again.",
        )

    try:
        payload = jwt.decode(
            token,
            settings.SECRET_KEY.get_secret_value(),
            algorithms=[settings.ALGORITHM],
        )
        username: str = payload.get("sub")
        if not username:
            raise credentials_exception

        token_data = schemas.TokenData(username=username)
    except ExpiredSignatureError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token has expired",
        )
    except InvalidTokenError:
        raise credentials_exception

    user = get_user(username=token_data.username, db=db)
    if user is None:
        raise credentials_exception

    return user


async def get_current_active_user(
    current_user: Annotated[models.UserORM, Depends(get_current_user)],
):
    if not current_user.is_active:
        raise HTTPException(status_code=400, detail="Inactive user")
    return current_user
