import io
import os
import sys
from contextlib import asynccontextmanager

import torch
import uvicorn
from fastapi import FastAPI, File, HTTPException, UploadFile, status
from fastapi.middleware.cors import CORSMiddleware
from PIL import Image

import image_vision_ai.app.schemas as schemas
from image_vision_ai.models.cnn_model import ImageClassifier

ml_models = {}

origins = [
    "http://localhost:3000",
]


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Load the ML model
    current_directory = os.path.dirname(os.path.abspath(__file__))
    parent_directory = os.path.dirname(current_directory)
    ml_models["image_classifier"] = ImageClassifier(
        model_path=parent_directory + "/models/mobilenet_v3_large.pth",
        categories_path=parent_directory + "/models/imagenet_classes.txt",
    )
    yield
    # Clean up the ML models and release the resources
    ml_models.clear()


# Initialize API Server
app = FastAPI(
    title="ImageVisionAI",
    description="Real-Time Image Classification Web Application",
    version="0.0.1",
    terms_of_service=None,
    contact=None,
    license_info={"name": "MIT", "url": "https://opensource.org/licenses/MIT"},
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.post(
    "/api/v1/predict/",
    status_code=status.HTTP_200_OK,
    response_model=schemas.InferenceResponse,
)
async def upload_image(file: UploadFile = File(...)):
    try:
        image_data = await file.read()
        image = Image.open(io.BytesIO(image_data))

        width, height = image.size
        category, prob = ml_models["image_classifier"].predict_category(image)
        results = {
            "filename": file.filename,
            "width": width,
            "height": height,
            "prediction": category,
            "probability": prob,
        }
        return schemas.InferenceResponse(error=False, results=results)

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An error occurred while classifying the image.",
        ) from e


@app.get("/api/v1/healthchecker")
def root():
    return {"message": "The API is LIVE!!"}


@app.get("/api/v1/about")
def show_about():
    """
    Get deployment information, for debugging
    """

    def bash(command):
        output = os.popen(command).read()
        return output

    return {
        "sys.version": sys.version,
        "torch.__version__": torch.__version__,
        "torch.cuda.is_available()": torch.cuda.is_available(),
        "torch.version.cuda": torch.version.cuda,
        "torch.backends.cudnn.version()": torch.backends.cudnn.version(),
        "torch.backends.cudnn.enabled": torch.backends.cudnn.enabled,
        "nvidia-smi": bash("nvidia-smi"),
    }


if __name__ == "__main__":
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8080,
        reload=True,
        debug=True,
        log_config="log.ini",
    )