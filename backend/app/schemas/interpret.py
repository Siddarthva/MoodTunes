from typing import Optional, Dict, Any, List
from pydantic import BaseModel, Field

class EmotionData(BaseModel):
    dominant: str = Field(..., description="Dominant emotion class name.")
    confidence: float = Field(..., description="Dominant emotion confidence percentage or score.")
    probabilities: Dict[str, float] = Field(..., description="7-class emotion probabilities.")

class EmotionalProfileData(BaseModel):
    energy: float = Field(..., description="Weighted energy value.")
    valence: float = Field(..., description="Weighted valence value.")
    tempo: str = Field(..., description="Derived tempo classification.")
    weighted_genres: Optional[List[Dict[str, Any]]] = Field(default=None, description="Weighted genre predictions.")

class InterpretMoodRequest(BaseModel):
    emotion: EmotionData = Field(..., description="Structured 7-class emotion probabilities.")
    emotional_profile: Optional[EmotionalProfileData] = Field(None, description="Derived emotional profile.")

class MusicDirectionOutput(BaseModel):
    energy: float = Field(default=50.0, description="Music direction energy.")
    valence: float = Field(default=50.0, description="Music direction valence.")
    tempo: str = Field(default="medium", description="Music direction tempo.")
    genres: List[str] = Field(default_factory=list, description="Suggested genres.")
    descriptors: List[str] = Field(default_factory=list, description="Atmospheric descriptors.")

class ConversationDirectionOutput(BaseModel):
    tone: str = Field(default="gentle, patient, reassuring", description="Conversational tone.")
    opening: str = Field(default="There seems to be a quieter weight to this moment. If you want, you can tell me what's on your mind.", description="Suggested opening message.")

class InterpretMoodResponse(BaseModel):
    success: bool = True
    headline: str = Field(..., description="Short contextual headline.")
    reflection: str = Field(..., description="Concise non-diagnostic reflection.")
    spectrum_summary: str = Field(..., description="Summary of primary & secondary emotions.")
    tone: str = Field(..., description="Identified comfort tone.")
    music_direction: MusicDirectionOutput = Field(..., description="Direction for soundtrack path.")
    conversation_direction: ConversationDirectionOutput = Field(..., description="Direction for conversation path.")
