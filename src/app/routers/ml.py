import io

from fastapi import APIRouter, File, HTTPException, UploadFile, status
from PIL import Image

from app.schemas import schemas

router: APIRouter = APIRouter()


@router.post(
    "/predict/",
    status_code=status.HTTP_200_OK,
    response_model=schemas.InferenceResponse,
)
async def predict(file: UploadFile = File(...)):
    from app.main import ml_models

    try:
        image_data = await file.read()
        image = Image.open(io.BytesIO(image_data))

        # Save image

        width, height = image.size
        category, prob = ml_models["image_classifier"].predict_category(image)
        results = schemas.InferenceResult(
            filename=str(file.filename),
            width=width,
            height=height,
            prediction=category,
            probability=prob,
        )
        return schemas.InferenceResponse(error=False, results=results)

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An error occurred while classifying the image.",
        ) from e
