from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from contextlib import asynccontextmanager

from app.core.config import settings
from app.core.exceptions import MoodTunesException
from app.api import health, analyze, music
from app.vision.face_detector import FaceDetector
from app.providers.emotion.mock import MockEmotionProvider
from app.providers.emotion.moodtunes_cnn import MoodTunesCNNProvider

@asynccontextmanager
async def lifespan(app: FastAPI):
    # 1. Initialize OpenCV Haar Cascade Face Detector
    app.state.face_detector = FaceDetector(cascade_path=settings.HAAR_CASCADE_PATH)
    
    # 2. Initialize Emotion Provider based on configured mode
    if settings.EMOTION_PROVIDER == "mock":
        app.state.emotion_provider = MockEmotionProvider()
        app.state.model_loaded = True
    else:
        try:
            app.state.emotion_provider = MoodTunesCNNProvider(
                model_path=settings.EMOTION_MODEL_PATH,
                labels_path=settings.EMOTION_LABELS_PATH
            )
            app.state.model_loaded = True
        except Exception as e:
            # Report model as unavailable so /health reflects truthful state
            app.state.emotion_provider = None
            app.state.model_loaded = False
            app.state.model_error = str(e)
            
    yield

app = FastAPI(
    title=settings.PROJECT_NAME,
    lifespan=lifespan
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.exception_handler(MoodTunesException)
async def moodtunes_exception_handler(request: Request, exc: MoodTunesException):
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "success": False,
            "error": {
                "code": exc.code,
                "message": exc.message
            }
        }
    )

app.include_router(health.router)
app.include_router(analyze.router, prefix="/api")
app.include_router(music.router, prefix="/api")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
