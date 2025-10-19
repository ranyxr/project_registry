from fastapi import FastAPI

from app.config import get_settings
from app.views import auth_router, project_router


def create_app() -> FastAPI:
    """Application factory used across run targets."""

    settings = get_settings()
    application = FastAPI(title=settings.app_name, debug=settings.debug)

    application.include_router(auth_router)
    application.include_router(project_router)

    return application


app = create_app()


@app.get("/health", tags=["health"])
def healthcheck():
    """Simple endpoint to monitor service health."""

    settings = get_settings()
    return {"status": "ok", "environment": settings.environment}
