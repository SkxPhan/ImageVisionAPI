# from typing import Any, Dict, List, Optional
from enum import Enum

from pydantic import BaseModel, Field


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


class InferenceResponse(BaseModel):
    """
    Output response for model inference
    """

    status: Status = Field(
        default=Status.Success,
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
