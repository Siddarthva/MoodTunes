from fastapi import APIRouter, Request
from app.core.config import settings

router = APIRouter()

@router.get("/health")
def health_check(request: Request):
    model_loaded = getattr(request.app.state, "model_loaded", False)
    return {
        "status": "ok",
        "project": settings.PROJECT_NAME,
        "model": {
            "provider": settings.EMOTION_PROVIDER,
            "loaded": model_loaded
        }
    }
