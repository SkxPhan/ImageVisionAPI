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

    filename: str = Field(..., title="Name of the file")
    width: int = Field(..., title="Image width")
    height: int = Field(..., title="Image height")
    prediction: str = Field(..., title="Image category")
    probability: float = Field(..., title="Image category probability")

    # model_config = ConfigDict(
    #     json_schema_extra={
    #         "examples": {
    #             "successful_inference": {
    #                 "filename": "dog.jpg",
    #                 "width": 640,
    #                 "height": 480,
    #                 "prediction": "Dog",
    #                 "probability": 0.9735,
    #             }
    #         }
    #     }
    # )


class InferenceResponse(BaseModel):
    """
    Output response for model inference
    """

    status: Status = Status.Success
    results: InferenceResult

    # model_config = ConfigDict(
    #     json_schema_extra={
    #         "examples": {
    #             "successful_response": {
    #                 "error": False,
    #                 "results": InferenceResult.model_config[
    #                     "json_schema_extra"
    #                 ]["examples"]["successful_inference"],
    #             }
    #         }
    #     }
    # )


class ErrorResponse(BaseModel):
    """
    Error response for the API
    """

    status: Status = Status.Error
    message: str = Field(..., title="Error message")
    traceback: str = Field(None, title="Detailed traceback of the error")

    # model_config = ConfigDict(
    #     json_schema_extra={
    #         "examples": {
    #             "error_case": {
    #                 "error": True,
    #                 "message": "An error occurred",
    #                 "traceback": "Traceback details here",
    #             }
    #         }
    #     }
    # )