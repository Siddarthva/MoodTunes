import httpx
from typing import List, Any
from app.providers.music.base import BaseMusicProvider
from app.schemas.analyze import Track
from app.providers.music.itunes import ITunesMusicProvider

class JamendoMusicProvider(BaseMusicProvider):
    """
    Jamendo Music API Provider v3.0 with iTunes fallback if client_id is missing or request fails.
    """
    BASE_URL = "https://api.jamendo.com/v3.0/tracks/"

    def __init__(self, client_id: str = ""):
        self.client_id = client_id
        self.fallback_provider = ITunesMusicProvider()

    async def fetch_candidates(self, mood: Any, query: str = None) -> List[Track]:
        if not self.client_id:
            # Fallback to iTunes seamlessly if Jamendo client ID is not configured
            return await self.fallback_provider.fetch_candidates(mood, query)

        params = {
            "client_id": self.client_id,
            "format": "json",
            "limit": 25,
            "include": "musicinfo",
            "audioformat": "mp32"
        }
        
        if query:
            params["search"] = query
        else:
            params["tags"] = mood.genres[0].lower()

        async with httpx.AsyncClient(timeout=8.0) as client:
            try:
                response = await client.get(self.BASE_URL, params=params)
                if response.status_code != 200:
                    return await self.fallback_provider.fetch_candidates(mood, query)

                data = response.json()
                results = data.get("results", [])
                
                if not results:
                    return await self.fallback_provider.fetch_candidates(mood, query)

                tracks: List[Track] = []
                for item in results:
                    track_id = str(item.get("id", ""))
                    if not track_id:
                        continue
                        
                    tracks.append(Track(
                        id=f"jamendo_{track_id}",
                        title=item.get("name", "Unknown Track"),
                        artist=item.get("artist_name", "Unknown Artist"),
                        album=item.get("album_name", "Single"),
                        genre=item.get("musicinfo", {}).get("gender", mood.genres[0]),
                        artworkUrl=item.get("album_image") or item.get("image") or "https://images.unsplash.com/photo-1511671782779-c97d3d27a1d4?w=300",
                        previewUrl=item.get("audio"),
                        source="Jamendo",
                        sourceUrl=item.get("shareurl"),
                        matchScore=90.0
                    ))
                return tracks
            except Exception:
                return await self.fallback_provider.fetch_candidates(mood, query)
