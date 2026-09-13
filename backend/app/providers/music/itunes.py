import httpx
from typing import List, Any
from app.providers.music.base import BaseMusicProvider
from app.schemas.analyze import Track

class ITunesMusicProvider(BaseMusicProvider):
    """
    iTunes Search API Provider (Zero Auth required, reliable preview URLs & artwork).
    """
    BASE_URL = "https://itunes.apple.com/search"

    async def fetch_candidates(self, mood: Any, query: str = None) -> List[Track]:
        search_terms = query if query else " ".join(mood.genres[:2])
        params = {
            "term": search_terms,
            "media": "music",
            "entity": "song",
            "limit": 20
        }
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
        }
        
        async with httpx.AsyncClient(timeout=4.0, headers=headers, follow_redirects=True) as client:
            try:
                response = await client.get(self.BASE_URL, params=params)
                if response.status_code != 200:
                    return []
                
                data = response.json()
                results = data.get("results", [])
                
                tracks: List[Track] = []
                for item in results:
                    track_id = str(item.get("trackId", ""))
                    if not track_id:
                        continue
                        
                    artwork = item.get("artworkUrl100", "").replace("100x100bb", "300x300bb")
                    preview_url = item.get("previewUrl")
                    
                    tracks.append(Track(
                        id=f"itunes_{track_id}",
                        title=item.get("trackName", "Unknown Track"),
                        artist=item.get("artistName", "Unknown Artist"),
                        album=item.get("collectionName", "Single"),
                        genre=item.get("primaryGenreName", mood.genres[0]),
                        artworkUrl=artwork or "https://images.unsplash.com/photo-1511671782779-c97d3d27a1d4?w=300",
                        previewUrl=preview_url,
                        source="iTunes",
                        sourceUrl=item.get("trackViewUrl"),
                        matchScore=85.0
                    ))
                return tracks
            except Exception as e:
                return []
