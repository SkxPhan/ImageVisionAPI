import os
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.core.config import settings
from app.core.ml.cnn_model import ImageClassifier
from app.db.database import init_db

origins = [
    "http://localhost:3000",
]

ml_models = {}


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


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Initialize the db
    init_db()

    # Load the ML model
    current_directory = os.path.dirname(os.path.abspath(__file__))
    parent_directory = os.path.dirname(current_directory)
    ml_models["image_classifier"] = ImageClassifier(
        model_path=os.path.join(parent_directory, settings.MODEL_PATH),
        label_path=os.path.join(parent_directory, settings.LABEL_PATH),
    )
    yield
    # Clean up the ML models and release the resources
    ml_models.clear()


def create_application(router, settings, create_tables_on_start=True, **kwargs):
    # Initialize API Server
    app = FastAPI(
        title="Image Classification Web API",
        description=description,
        summary="Web API for image classification",
        version="0.1.0",
        terms_of_service=None,
        contact={"name": "SkxPhan", "url": "https://github.com/SkxPhan"},
        license_info={
            "name": "MIT",
            "url": "https://opensource.org/licenses/MIT",
        },
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
    app.include_router(router)
    return app
