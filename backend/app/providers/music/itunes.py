import httpx
import logging
from typing import List, Any
from app.providers.music.base import BaseMusicProvider
from app.schemas.analyze import Track

logger = logging.getLogger(__name__)

class ITunesMusicProvider(BaseMusicProvider):
    """
    iTunes Search API Provider (Zero Auth required, reliable preview URLs & artwork).
    """
    BASE_URL = "https://itunes.apple.com/search"

    async def fetch_candidates(self, mood: Any, direction: Any = None, query: str = None) -> List[Track]:
        queries_to_run = []
        if query:
            queries_to_run = [query]
        elif direction and getattr(direction, "search_queries", None):
            queries_to_run = direction.search_queries[:3]  # take top 3 queries
        else:
            top_genre = mood.weighted_genres[0].genre if (hasattr(mood, "weighted_genres") and mood.weighted_genres) else "Pop"
            queries_to_run = [top_genre]

        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
        }
        
        all_tracks = []
        seen_ids = set()

        async with httpx.AsyncClient(timeout=4.0, headers=headers, follow_redirects=True) as client:
            for q in queries_to_run:
                params = {
                    "term": q,
                    "media": "music",
                    "entity": "song",
                    "limit": 15
                }
                
                try:
                    response = await client.get(self.BASE_URL, params=params)
                    if response.status_code != 200:
                        continue
                    
                    data = response.json()
                    results = data.get("results", [])
                    
                    for item in results:
                        track_id = str(item.get("trackId", ""))
                        if not track_id or track_id in seen_ids:
                            continue
                            
                        seen_ids.add(track_id)
                        artwork = item.get("artworkUrl100", "").replace("100x100bb", "300x300bb")
                        preview_url = item.get("previewUrl")
                        
                        all_tracks.append(Track(
                            id=f"itunes_{track_id}",
                            title=item.get("trackName", "Unknown Track"),
                            artist=item.get("artistName", "Unknown Artist"),
                            album=item.get("collectionName", "Single"),
                            genre=item.get("primaryGenreName", "Pop"),
                            artworkUrl=artwork or "https://images.unsplash.com/photo-1511671782779-c97d3d27a1d4?w=300",
                            previewUrl=preview_url,
                            source="iTunes",
                            sourceUrl=item.get("trackViewUrl"),
                            matchScore=85.0,
                            duration_ms=item.get("trackTimeMillis", 0),
                            playable=bool(preview_url),
                            source_metadata={"query_used": q}
                        ))
                except Exception as e:
                    logger.error(f"iTunes API Error on query '{q}': {e}")
                    continue

        return all_tracks
