from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

import app.models as models
from app.api.dependencies import get_current_active_user
from app.db.database import get_db
from app.schemas import schemas

router: APIRouter = APIRouter(prefix="/users", tags=["User"])


@router.get(
    "/me",
    response_description="Information of the current user",
)
async def get_user_info(
    current_user: Annotated[
        schemas.UserCreate, Depends(get_current_active_user)
    ]
) -> schemas.UserResponse:
    return current_user


@router.get(
    "/me/history",
    response_description="Most recent image classification history",
)
async def get_classification_history(
    current_user: Annotated[models.UserORM, Depends(get_current_active_user)],
    db: Annotated[Session, Depends(get_db)],
    limit: Annotated[int, Query(description="Number of images to fetch")] = 5,
) -> schemas.InferenceResultHistoryResponse:
    try:
        images = (
            db.query(models.ImageORM)
            .filter(models.ImageORM.user_id == current_user.id)
            .order_by(models.ImageORM.creationdate.desc())
            .limit(limit)
            .all()
        )
        history = [
            schemas.InferenceResultHistory(
                filename=image.filename,
                label=image.label,
                probability=image.probability,
                upload_timestamp=image.creationdate,
            )
            for image in images
        ]
        return schemas.InferenceResultHistoryResponse(
            status=schemas.Status.Success,
            username=current_user.username,
            history=history,
        )

    except Exception as e:
        print(e)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An error occurred while retrieving classification history",
        ) from e
