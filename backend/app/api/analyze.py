from fastapi import APIRouter, UploadFile, File, Request, HTTPException
from fastapi.concurrency import run_in_threadpool
from app.schemas.analyze import AnalyzeResponse, ErrorResponse
from app.core.exceptions import InvalidImageException, ModelNotReadyException
from app.services.mood_service import MoodService
from app.services.recommendation_service import RecommendationService
from app.providers.music.jamendo import JamendoMusicProvider
from app.providers.music.itunes import ITunesMusicProvider
from app.core.config import settings

router = APIRouter()

MAX_FILE_SIZE = 10 * 1024 * 1024  # 10 MB

@router.post("/analyze", response_model=AnalyzeResponse, responses={400: {"model": ErrorResponse}, 422: {"model": ErrorResponse}, 503: {"model": ErrorResponse}})
async def analyze_expression(request: Request, image: UploadFile = File(...)):
    # 1. Validate payload
    if not image or not image.filename:
        raise InvalidImageException("No image file provided in field 'image'.")
        
    contents = await image.read()
    if not contents or len(contents) == 0:
        raise InvalidImageException("Uploaded file is empty.")

    if len(contents) > MAX_FILE_SIZE:
        raise HTTPException(status_code=400, detail="Image file exceeds maximum limit of 10MB.")

    # 2. Check Emotion Provider State
    emotion_provider = getattr(request.app.state, "emotion_provider", None)
    if not emotion_provider:
        err_msg = getattr(request.app.state, "model_error", "Emotion recognition model is currently unavailable.")
        raise ModelNotReadyException(err_msg)

    face_detector = getattr(request.app.state, "face_detector", None)

    # 3. Vision Pipeline: Haar Cascade Face Detection & Primary Face Crop
    img_bgr, bbox = await run_in_threadpool(face_detector.detect_largest_face, contents)
    
    # 4. Preprocessing (Grayscale, 48x48, Float32 / 255.0, Reshape tensor shape (1,48,48,1))
    from app.vision.preprocessor import preprocess_face
    face_tensor = await run_in_threadpool(preprocess_face, img_bgr, bbox)

    # 5. Emotion Model Inference
    emotion_result = await run_in_threadpool(emotion_provider.predict, face_tensor)

    # 6. Emotion -> Mood Profile Mapping
    emotional_profile = MoodService.calculate_emotional_profile(
        dominant_emotion=emotion_result.dominant,
        probabilities=emotion_result.probabilities.model_dump()
    )

    # 7. Music Provider & Recommendation Engine
    if settings.MUSIC_PROVIDER == "jamendo":
        music_provider = JamendoMusicProvider(client_id=settings.JAMENDO_CLIENT_ID)
    else:
        music_provider = ITunesMusicProvider()
        
    rec_service = RecommendationService(music_provider=music_provider)
    recommendations = await rec_service.get_recommendations(profile=emotional_profile)

    # 8. Return Pydantic Response matching API contract
    return AnalyzeResponse(
        success=True,
        emotion=emotion_result,
        emotional_profile=emotional_profile,
        recommendations=recommendations
    )
