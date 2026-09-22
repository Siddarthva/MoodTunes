from fastapi import APIRouter
from app.services.groq_content_service import GroqContentService
from app.core.config import settings
from app.schemas.mood_content import MoodContentRequest, MoodContentResponse, PostScanContentResponse
import time
from typing import Dict, Any

router = APIRouter()
groq_content_service = GroqContentService()

# Simple in-memory cache
_content_cache: Dict[str, Any] = {}
_cache_timestamp: float = 0
CACHE_DURATION = settings.CONTENT_CACHE_MINUTES * 60

@router.get("/content/home")
async def get_home_content():
    global _content_cache, _cache_timestamp
    
    now = time.time()
    
    # Return cached content if valid
    if _content_cache and (now - _cache_timestamp) < CACHE_DURATION:
        return _content_cache

    # Otherwise fetch new content
    new_content = await groq_content_service.generate_home_content()
    
    # Update cache
    _content_cache = new_content
    _cache_timestamp = now
    
    
    return new_content

@router.post("/content/mood", response_model=MoodContentResponse)
async def generate_mood_content(request: MoodContentRequest):
    response = await groq_content_service.generate_mood_content(request)
    return response

@router.post("/content/post-scan", response_model=PostScanContentResponse)
async def generate_post_scan_content(request: MoodContentRequest):
    response = await groq_content_service.generate_post_scan_content(request)
    return response

@router.post("/mood/interpret")
async def interpret_mood_endpoint(request: Dict[str, Any]):
    return await groq_content_service.interpret_mood(request)

