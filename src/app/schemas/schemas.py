# from typing import Any, Dict, List, Optional
from enum import Enum

from pydantic import BaseModel, EmailStr, Field, field_validator


class Status(str, Enum):
    Success = "Success"
    Error = "Error"


class InferenceResult(BaseModel):
    """
    Inference result from the model
    """

    filename: str = Field(
        ...,
        title="Name of the file",
        json_schema_extra={
            "example": "dog.png",
            "description": "Name of the file",
        },
    )
    width: int = Field(
        ...,
        title="Image width",
        json_schema_extra={
            "example": 640,
            "description": "Image width",
        },
    )
    height: int = Field(
        ...,
        title="Image height",
        json_schema_extra={
            "example": 480,
            "description": "Image height",
        },
    )
    prediction: str = Field(
        ...,
        title="Image category",
        json_schema_extra={
            "example": "Dog",
            "description": "Image category",
        },
    )
    probability: float = Field(
        ...,
        title="Image category probability",
        json_schema_extra={
            "example": "0.9735",
            "description": "Image category probability",
        },
    )

    @field_validator("probability")
    def probability_format(cls, v):
        ...
        return round(v, 5)


class InferenceResponse(BaseModel):
    """
    Output response for model inference
    """

    status: Status = Field(
        ...,
        description="The status of the operation",
    )
    results: InferenceResult


class ErrorResponse(BaseModel):
    """
    Error response for the API
    """

    status: Status = Field(
        default=Status.Error,
        description="The status of the operation",
    )
    message: str = Field(
        ...,
        title="Error message",
        json_schema_extra={
            "example": "An error occurred",
            "description": "Error message",
        },
    )
    traceback: str = Field(
        None,
        title="Detailed traceback of the error",
        json_schema_extra={
            "example": "Traceback details here",
            "description": "Detailed traceback of the error",
        },
    )


class UserCreate(BaseModel):
    username: str = Field(
        ...,
        title="Username",
        json_schema_extra={
            "example": "JohnDoe",
            "description": "Username",
        },
    )
    email: EmailStr = Field(
        ...,
        title="Email address",
        json_schema_extra={
            "example": "example@example.com",
            "description": "Email address",
        },
    )
    password: str = Field(
        ...,
        title="Password",
        json_schema_extra={
            "example": "Password",
            "description": "Password of minimum 8 characters.",
        },
    )
    is_active: bool = Field(
        default=True,
        json_schema_extra={
            "example": "true",
            "description": "Indicates whether the user account is active or"
            " not",
        },
    )

    @field_validator("email")
    def email_format(cls, v):
        if "@" not in v or "." not in v.split("@")[-1]:
            raise ValueError("Invalid email address format")
        return v

    @field_validator("password")
    def password_length(cls, v):
        if len(v) < 8:
            raise ValueError("Password must be at least 8 characters long")
        return v


class RegisterResponse(BaseModel):
    status: Status = Field(
        ...,
        description="The status of the operation",
    )
    message: str = Field(
        ...,
        title="Message confirmation",
        json_schema_extra={
            "example": "User JohnDoe registered successfully.",
            "description": "Confirmation message with the username of the"
            " registered user.",
        },
    )


class User(BaseModel):
    username: str
    email: str
    is_active: bool


class UserInDB(User):
    hashed_password: str


class Token(BaseModel):
    access_token: str
    token_type: str


class TokenData(BaseModel):
    username: str | None = None
