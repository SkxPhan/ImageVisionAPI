from typing import Any, Dict, List, Optional

from pydantic import BaseModel, Field


class InferenceResult(BaseModel):
    """
    Inference result from the model
    """

    filename: str = Field(..., example="dog.jpg", title="Name of the file")
    width: int = Field(..., example=640, title="Image width")
    height: int = Field(..., example=480, title="Image height")
    prediction: str = Field(..., example="Dog", title="Image category")
    probability: float = Field(
        ..., example="0.9735", title="Image category probability"
    )


class InferenceResponse(BaseModel):
    """
    Output response for model inference
    """

    error: bool = Field(..., example=False, title="Whether there is error")
    results: InferenceResult


class ErrorResponse(BaseModel):
    """
    Error response for the API
    """

    error: bool = Field(..., example=True, title="Whether there is error")
    message: str = Field(..., example="", title="Error message")
    traceback: str = Field(
        None, example="", title="Detailed traceback of the error"
    )
