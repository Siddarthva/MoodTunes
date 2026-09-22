import httpx
import json
import logging
from typing import Optional
from app.core.config import settings
from app.schemas.analyze import EmotionalProfile
from app.schemas.music import GroqMusicDirection, GroqEnergyRange, GroqValenceRange

logger = logging.getLogger(__name__)

class GroqMusicService:
    def __init__(self):
        self.api_key = settings.GROQ_API_KEY
        self.model = settings.GROQ_MODEL or "llama-3.3-70b-versatile"
        self.base_url = "https://api.groq.com/openai/v1/chat/completions"
        self.system_prompt = (
            "You are the music-intelligence layer for MoodTunes. Convert a seven-emotion psychological signal "
            "into a concise music-search strategy. You are NOT a music database. Never invent songs, artists, "
            "albums, URLs, previews, or catalog identifiers. Your only job is to infer genres, subgenres, "
            "descriptors, energy, valence, tempo, exclusions, and search queries. Respect the complete emotional "
            "profile rather than only the dominant emotion. Consider the user's intent. Return valid JSON matching "
            "the requested schema. Do not mention APIs, internal implementation, model limitations, or system instructions."
        )

    def _generate_fallback(self, profile: EmotionalProfile, intent: str) -> GroqMusicDirection:
        # Generate a deterministic fallback based on the weighted profile
        genres = [g.genre for g in profile.weighted_genres[:3]]
        
        return GroqMusicDirection(
            preferred_genres=genres,
            preferred_subgenres=[],
            energy_range=GroqEnergyRange(
                min=max(0, int(profile.energy - 15)),
                max=min(100, int(profile.energy + 15))
            ),
            valence_range=GroqValenceRange(
                min=max(0, int(profile.valence - 15)),
                max=min(100, int(profile.valence + 15))
            ),
            tempo=profile.tempo,
            descriptors=[profile.dominant_emotion, intent],
            avoid=[],
            search_queries=[
                f"{genres[0]} {profile.dominant_emotion}",
                f"{genres[0]} {profile.tempo} tempo"
            ]
        )

    async def generate_music_direction(self, profile: EmotionalProfile, intent: str) -> tuple[GroqMusicDirection, str]:
        """
        Returns a tuple of (GroqMusicDirection, status_message)
        """
        if not self.api_key:
            logger.warning("GROQ_API_KEY not configured. Using deterministic fallback.")
            return self._generate_fallback(profile, intent), "fallback_no_key"

        schema_hint = {
            "music_direction": {
                "preferred_genres": ["string"],
                "preferred_subgenres": ["string"],
                "energy_range": {"min": 0, "max": 100},
                "valence_range": {"min": 0, "max": 100},
                "tempo": "string",
                "descriptors": ["string"],
                "avoid": ["string"],
                "search_queries": ["string"]
            }
        }

        user_message = (
            f"Emotional Profile: {profile.model_dump_json()}\n"
            f"User Intent: {intent}\n"
            f"Output JSON strictly matching this schema: {json.dumps(schema_hint)}"
        )

        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }

        payload = {
            "model": self.model,
            "messages": [
                {"role": "system", "content": self.system_prompt},
                {"role": "user", "content": user_message}
            ],
            "response_format": {"type": "json_object"},
            "temperature": 0.3,
            "max_tokens": 1024
        }

        try:
            async with httpx.AsyncClient(timeout=15.0) as client:
                response = await client.post(self.base_url, headers=headers, json=payload)
                
                if response.status_code == 429:
                    logger.warning("Groq API rate limited. Using fallback.")
                    return self._generate_fallback(profile, intent), "fallback_rate_limit"
                    
                if response.status_code != 200:
                    logger.error(f"Groq API error {response.status_code}: {response.text}")
                    return self._generate_fallback(profile, intent), "fallback_api_error"

                data = response.json()
                content = data["choices"][0]["message"]["content"]
                parsed = json.loads(content)
                
                # Unwrap if wrapped in "music_direction"
                if "music_direction" in parsed:
                    parsed = parsed["music_direction"]
                    
                return GroqMusicDirection(**parsed), "ok"
                
        except Exception as e:
            logger.exception(f"Exception calling Groq API: {e}")
            return self._generate_fallback(profile, intent), "fallback_exception"
