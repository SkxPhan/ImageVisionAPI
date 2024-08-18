from enum import Enum

from pydantic import BaseModel, EmailStr, Field, field_validator


class Status(str, Enum):
    """
    Status of the operation.
    """

    Success = "Success"
    Error = "Error"


class InferenceResult(BaseModel):
    """
    Inference result schema from the model.
    """

    filename: str = Field(description="Filename", examples=["dog.png"])
    width: int = Field(description="Image width", examples=[640], gt=0.0)
    height: int = Field(description="Image height", examples=[480], gt=0.0)
    prediction: str = Field(description="Image category", examples=["Dog"])
    probability: float | None = Field(
        description="Image category probability",
        examples=[0.9735],
        ge=0.0,
        le=1.0,
    )

    @field_validator("probability")
    def probability_format(cls, v):
        return round(v, 5)


class InferenceResponse(BaseModel):
    """
    Response shema when classifying an image.
    """

    status: Status
    results: InferenceResult


class RegisterResponse(BaseModel):
    """
    Response schema when a user registers.
    """

    status: Status
    message: str = Field(
        description="Registration confirmation",
        examples=["User JohnDoe registered successfully."],
    )


class UserCreate(BaseModel):
    """
    Input schema for creating a new user.
    """

    username: str = Field(
        description="Username",
        examples=["JohnDoe"],
    )
    email: EmailStr = Field(
        description="Email address",
        examples=["example@example.com"],
    )
    password: str = Field(
        description="Password", examples=["Password"], exclude=True
    )
    is_active: bool = Field(
        default=True,
        description="Indicates if the user account is active",
        examples=[True],
    )

    @field_validator("email")
    def email_format(cls, v):
        if "@" not in v or "." not in v.split("@")[-1]:
            raise ValueError("Invalid email address format.")
        return v

    @field_validator("password")
    def password_length(cls, v):
        if len(v) < 8:
            raise ValueError("Password must be at least 8 characters long.")
        return v


class UserResponse(UserCreate):
    """
    Response schema when requesting an user.
    """

    pass


class Token(BaseModel):
    """
    Response schema when requesting an token.
    """

    access_token: str
    token_type: str


class TokenData(BaseModel):
    """
    Token schema.
    """

    username: str | None = None


class ErrorResponse(BaseModel):
    """
    Error response schema.
    """

    status: Status = Status.Error
    message: str = Field(
        description="Error message",
        examples=["An error occurred"],
    )
    traceback: str = Field(
        None,
        description="Detailed traceback of the error",
        examples=["Traceback details here"],
    )
