from pydantic import BaseModel, Field
from typing import List

class GroqEnergyRange(BaseModel):
    min: int = Field(..., ge=0, le=100)
    max: int = Field(..., ge=0, le=100)

class GroqValenceRange(BaseModel):
    min: int = Field(..., ge=0, le=100)
    max: int = Field(..., ge=0, le=100)

class GroqMusicDirection(BaseModel):
    preferred_genres: List[str]
    preferred_subgenres: List[str]
    energy_range: GroqEnergyRange
    valence_range: GroqValenceRange
    tempo: str
    descriptors: List[str]
    avoid: List[str]
    search_queries: List[str]
