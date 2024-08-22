import os
import sys
from contextlib import asynccontextmanager

import torch
import uvicorn
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.database import init_db
from app.ml.cnn_model import ImageClassifier
from app.routers import auth, ml

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


description = """
ImageVisionAPI helps you do awesome stuff. 🚀

## Machine Learning

You can **classify** images.

## Users

You will be able to:

* **Create users**.
* **Classify images**.
* **Vizualize history of previous classifications** (_not implemented_).
"""

tags_metadata = [
    {
        "name": "Auth",
        "description": "Registration, login and logout",
    },
    {
        "name": "ML",
        "description": "Image classification using **AI**.",
    },
    {
        "name": "Info",
        "description": "Miscellaneous information.",
    },
]

# Initialize API Server
app = FastAPI(
    title="Image Classification Web API",
    description=description,
    summary="Web API for image classification",
    version="0.1.0",
    terms_of_service=None,
    contact={"name": "SkxPhan", "url": "https://github.com/SkxPhan"},
    license_info={"name": "MIT", "url": "https://opensource.org/licenses/MIT"},
    lifespan=lifespan,
    openapi_tags=tags_metadata,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(ml.router, tags=["ML"], prefix="/api/v1/ml")
app.include_router(auth.router, tags=["Auth"], prefix="/api/v1/auth")


@app.get(
    "/",
    tags=["Info"],
    summary="API Live Checker",
    response_description="Confirmation",
)
def healthchecker():
    """
    Simple endpoint to check that the API is live.
    """
    return {"message": "The API is LIVE!"}


@app.get(
    "/about",
    tags=["Info"],
    response_description="System information",
)
def show_system_info():
    """
    Get information about the environment and PyTorch version, for debugging.
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
