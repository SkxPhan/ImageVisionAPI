import uvicorn

from app.api import router
from app.core.config import settings
from app.core.setup import create_application

app = create_application(router=router, settings=settings)

if __name__ == "__main__":
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_config="logging.ini",
    )
