from typing import Optional, Dict, Any
from pydantic import BaseModel, Field

class MoodContentRequest(BaseModel):
    dominant_emotion: str = Field(..., description="The dominant predicted emotion class.")
    emotional_profile: Dict[str, Any] = Field(..., description="The full 7-class profile and weighted attributes.")
    energy: float = Field(..., description="The calculated energy level (0-1).")
    valence: float = Field(..., description="The calculated valence level (0-1).")
    intent: Optional[str] = Field(None, description="The user's listening intent.")

class MoodContentResponse(BaseModel):
    quote: str = Field(..., description="A short, poetic, uplifting quote related to the mood.")
    interpretation: str = Field(..., description="A 1-2 sentence human editorial interpretation.")
    small_line: str = Field(..., description="A very short micro-copy statement.")
    success: bool = True

class PostScanContentResponse(BaseModel):
    quote: str = Field(..., description="A large uplifting quote or headline to show after recommendations.")
    reflection: str = Field(..., description="A short reflective paragraph related to the emotional profile.")
    headline: Optional[str] = Field(None, description="Short contextual phrase <= 10 words")
    music_intro: Optional[str] = Field(None, description="Short recommendation intro phrase <= 18 words")
    tone: Optional[str] = Field(None, description="The identified emotional tone")
    visual_direction: Optional[str] = Field(None, description="Visual theme direction")
    success: bool = True
