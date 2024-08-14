import os
import sys
from contextlib import asynccontextmanager

import torch
import uvicorn
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.database import init_db
from app.ml.cnn_model import ImageClassifier
from app.routers import ml

origins = [
    "http://localhost:3000",
]

ml_models = {}


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Initialize the db
    init_db()

    # Load the ML model
    current_directory = os.path.dirname(os.path.abspath(__file__))
    ml_models["image_classifier"] = ImageClassifier(
        model_path=current_directory + "/ml/mobilenet_v3_large.pth",
        categories_path=current_directory + "/ml/imagenet_classes.txt",
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

app.include_router(ml.router, tags=["ML"], prefix="/api/v1/ml")


@app.get("/api/healthchecker")
def healthchecker():
    return {"message": "The API is LIVE!"}


@app.get("/api/about")
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
        port=8000,
        reload=True,
        log_config="logging.ini",
    )
