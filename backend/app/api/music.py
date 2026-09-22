from fastapi import APIRouter, Query
from typing import List, Optional
from app.schemas.analyze import Track
from app.services.mood_service import MoodService
from app.services.recommendation_service import RecommendationService
from app.providers.music.itunes import ITunesMusicProvider
from app.core.config import settings

router = APIRouter()

def get_recommendation_service() -> RecommendationService:
    provider = ITunesMusicProvider()
    return RecommendationService(music_provider=provider)

@router.get("/music/search", response_model=List[Track])
async def search_music(q: str = Query(..., min_length=1)):
    rec_service = get_recommendation_service()
    neutral_mood = MoodService.get_mood_for_emotion("neutral")
    return await rec_service.get_recommendations(profile=neutral_mood, query=q)

@router.get("/music/recommendations", response_model=List[Track])
async def get_recommendations(emotion: Optional[str] = "happy"):
    rec_service = get_recommendation_service()
    mood = MoodService.get_mood_for_emotion(emotion)
    return await rec_service.get_recommendations(profile=mood)
