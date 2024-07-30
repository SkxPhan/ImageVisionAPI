import io
from contextlib import asynccontextmanager

import uvicorn
from fastapi import FastAPI, File, UploadFile
from models.cnn_model import ImageClassifier
from PIL import Image


ml_models = {}


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Load the ML model
    ml_models["image_classifier"] = ImageClassifier(
        model_path="models/mobilenet_v3_large.pth",
        categories_path="models/imagenet_classes.txt",
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


@app.post("/api/v1/predict/")
async def upload_image(file: UploadFile = File(...)):
    image_data = await file.read()
    image = Image.open(io.BytesIO(image_data))

    width, height = image.size
    category, prob = ml_models["image_classifier"].predict_category(image)

    return {
        "filename": file.filename,
        "width": width,
        "height": height,
        "prediction": category,
        "probability": prob,
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
