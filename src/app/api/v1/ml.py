import io
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, UploadFile, status
from PIL import Image
from sqlalchemy.orm import Session

import app.models as models
from app.api.dependencies import get_current_active_user
from app.db.database import get_db
from app.schemas import schemas

router: APIRouter = APIRouter(prefix="/ml", tags=["ML"])


@router.post(
    "/predict",
    status_code=status.HTTP_200_OK,
    response_description="Classify an image using CNN",
)
async def predict(
    file: UploadFile,
    db: Annotated[Session, Depends(get_db)],
    current_user: Annotated[models.UserORM, Depends(get_current_active_user)],
) -> schemas.InferenceResponse:
    from app.core.setup import ml_models

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
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An error occurred while classifying the image.",
        ) from e

    try:
        new_image = models.ImageORM(
            filename=file.filename,
            image_data=image_data,
            label=category,
            probability=prob,
            user_id=current_user.id,
        )
        db.add(new_image)
        db.commit()
        db.refresh(new_image)
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An error occurred while saving the image.",
        ) from e

    return schemas.InferenceResponse(
        status=schemas.Status.Success, results=results
    )
