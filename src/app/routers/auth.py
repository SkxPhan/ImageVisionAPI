import os
from datetime import datetime, timedelta, timezone
from typing import Annotated, Any, Literal

import bcrypt
import jwt
from dotenv import load_dotenv
from fastapi import APIRouter, Depends, HTTPException, Response, status
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from jose import JWTError
from jwt.exceptions import ExpiredSignatureError, InvalidTokenError
from sqlalchemy.orm import Session

import app.models as models
from app.database import TokenBlacklistORM, get_db
from app.schemas import schemas

router: APIRouter = APIRouter()

# run: openssl rand -hex 32
load_dotenv()
SECRET_KEY = os.getenv("SECRET_KEY")
ALGORITHM = os.getenv("ALGORITHM", "HS256")
ACCESS_TOKEN_EXPIRE_MINUTES = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", 30))

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/v1/auth/login")


def get_password_hash(password: str) -> str:
    hashed_password: str = bcrypt.hashpw(
        password.encode(), bcrypt.gensalt()
    ).decode()
    return hashed_password


def verify_password(plain_password: str, hashed_password: str) -> bool:
    correct_password: bool = bcrypt.checkpw(
        plain_password.encode(), hashed_password.encode()
    )
    return correct_password


def get_user(username: str | None, db: Session) -> models.UserORM | None:
    if username is None:
        return None

    user = (
        db.query(models.UserORM)
        .filter(models.UserORM.username == username)
        .first()
    )

    return user or None


def authenticate_user(
    username: str, password: str, db: Session
) -> models.UserORM | Literal[False]:
    user = get_user(username, db)
    if not user:
        return False
    elif not verify_password(password, user.hashed_password):
        return False
    return user


def create_access_token(
    data: dict[str, Any], expires_delta: timedelta | None = None
) -> str:
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.now(timezone.utc) + expires_delta
    else:
        expire = datetime.now(timezone.utc) + timedelta(
            minutes=ACCESS_TOKEN_EXPIRE_MINUTES
        )
    to_encode.update({"exp": expire})
    encoded_jwt: str = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt


def get_current_user(
    token: Annotated[str, Depends(oauth2_scheme)],
    db: Annotated[Session, Depends(get_db)],
):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        is_blacklisted = (
            db.query(TokenBlacklistORM)
            .filter(TokenBlacklistORM.token == token)
            .first()
            is not None
        )
        if is_blacklisted:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Token has been blacklisted",
            )

        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
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


def blacklist_token(token: str, db: Session) -> None:
    from app.database import TokenBlacklistORM

    payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
    expires_at = datetime.fromtimestamp(payload.get("exp"))
    token_blacklist = TokenBlacklistORM(token=token, expires_at=expires_at)
    db.add(token_blacklist)
    db.commit()


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
    try:
        hashed_password = get_password_hash(user.password.get_secret_value())
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
    # Add exeption if user already in db!
    except Exception:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An error occurred while registering the user.",
        )


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
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
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
) -> Response:
    try:
        blacklist_token(token=access_token, db=db)
        return {"message": "Logged out successfully"}
    except JWTError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token.",
            headers={"WWW-Authenticate": "Bearer"},
        )


@router.get(
    "/users/me",
    response_description="Information of the current user",
)
async def get_user_info(
    current_user: Annotated[
        schemas.UserCreate, Depends(get_current_active_user)
    ]
) -> schemas.UserResponse:
    return current_user
