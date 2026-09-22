from pydantic import BaseModel, Field
from typing import Dict, List, Optional

from app.schemas.music import GroqMusicDirection

class EmotionProbabilities(BaseModel):
    angry: float = Field(..., ge=0, le=100)
    disgust: float = Field(..., ge=0, le=100)
    fear: float = Field(..., ge=0, le=100)
    happy: float = Field(..., ge=0, le=100)
    sad: float = Field(..., ge=0, le=100)
    surprise: float = Field(..., ge=0, le=100)
    neutral: float = Field(..., ge=0, le=100)

class EmotionResult(BaseModel):
    dominant: str
    confidence: float
    probabilities: EmotionProbabilities

class GenreWeight(BaseModel):
    genre: str
    weight: float

class EmotionalProfile(BaseModel):
    dominant_emotion: str
    energy: float = Field(..., ge=0, le=100)
    valence: float = Field(..., ge=0, le=100)
    tempo: str
    weighted_genres: List[GenreWeight]

class Track(BaseModel):
    id: str
    title: str
    artist: str
    album: str
    genre: str
    artworkUrl: str
    previewUrl: Optional[str] = None
    source: str
    sourceUrl: Optional[str] = None
    matchScore: float
    duration_ms: Optional[int] = 0
    playable: bool = False
    source_metadata: Dict = Field(default_factory=dict)

class AnalyzeResponse(BaseModel):
    success: bool = True
    emotion: EmotionResult
    emotional_profile: EmotionalProfile
    user_intent: str = "match_me"
    music_direction: Optional[GroqMusicDirection] = None
    provider_status: Dict[str, str] = Field(default_factory=dict)
    recommendations: List[Track]

class ErrorDetail(BaseModel):
    code: str
    message: str

class ErrorResponse(BaseModel):
    success: bool = False
    error: ErrorDetail
