import os
import sys

import torch
from fastapi import APIRouter

router: APIRouter = APIRouter(tags=["Info"])


@router.get(
    "/",
    summary="API Live Checker",
    response_description="Confirmation",
)
def healthchecker():
    """
    Simple endpoint to check that the API is live.
    """
    return {"message": "The API is LIVE!"}


@router.get(
    "/about",
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
        "nvidia-smi": (
            bash("nvidia-smi")
            if torch.cuda.is_available()
            else "CUDA not available"
        ),
    }
