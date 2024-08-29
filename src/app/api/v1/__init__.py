from fastapi import APIRouter

from .auth import router as auth_router
from .info import router as info_router
from .ml import router as ml_router
from .users import router as users_router

router = APIRouter(prefix="/v1")
router.include_router(auth_router)
router.include_router(ml_router)
router.include_router(info_router)
router.include_router(users_router)
