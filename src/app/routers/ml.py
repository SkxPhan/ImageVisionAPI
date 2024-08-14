import io

from fastapi import APIRouter, Depends, File, HTTPException, UploadFile, status
from PIL import Image
from sqlalchemy.orm import Session

import app.models as models
from app.database import get_db
from app.schemas import schemas

router: APIRouter = APIRouter()


@router.post(
    "/predict/",
    status_code=status.HTTP_200_OK,
    response_model=schemas.InferenceResponse,
)
async def predict(file: UploadFile = File(...), db: Session = Depends(get_db)):
    from app.main import ml_models

    try:
        image_data = await file.read()

        image = Image.open(io.BytesIO(image_data))
        width, height = image.size
        category, prob = ml_models["image_classifier"].predict_category(image)
        results = schemas.InferenceResult(
            filename=str(file.filename),
            width=width,
            height=height,
            prediction=category,
            probability=prob,
        )
    except Exception:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An error occurred while classifying the image.",
        )

    try:
        new_image = models.ImageORM(
            filename=file.filename,
            image_data=image_data,
            classification=category,
            probability=prob,
        )
        db.add(new_image)
        db.commit()
        db.refresh(new_image)
    except Exception:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An error occurred while saving the image.",
        )

    return schemas.InferenceResponse(
        status=schemas.Status.Success, results=results
    )
