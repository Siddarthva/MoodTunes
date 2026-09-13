from typing import List
from app.schemas.analyze import Track, EmotionalProfile
from app.providers.music.base import BaseMusicProvider

class RecommendationService:
    """
    Ranks candidate tracks using composite weighted scoring based on emotional profile alignment,
    genre matching, and audio preview playability.
    """
    def __init__(self, music_provider: BaseMusicProvider):
        self.music_provider = music_provider

    def _score_track(self, track: Track, profile: EmotionalProfile) -> float:
        # 1. Emotion Profile Match Score (30%)
        # Sum the weights of matching genres from the profile
        profile_match_score = 0.0
        for gw in profile.weighted_genres:
            if gw.genre.lower() in track.genre.lower():
                profile_match_score += gw.weight
                
        # Ensure a baseline of 60.0 for fallback and cap at 100.0
        profile_match_score = min(100.0, max(60.0, profile_match_score))
        
        # 2. Genre Alignment Score (25%)
        top_genre = profile.weighted_genres[0].genre.lower() if profile.weighted_genres else ""
        genre_score = 95.0 if top_genre in track.genre.lower() else 75.0
        
        # 3. Energy Score (20%)
        energy_score = float(profile.energy)
        
        # 4. Valence Score (15%)
        valence_score = float(profile.valence)
        
        # 5. Playability Score (10%)
        playability_score = 100.0 if track.previewUrl else 0.0
        
        composite = (
            (profile_match_score * 0.30) +
            (genre_score * 0.25) +
            (energy_score * 0.20) +
            (valence_score * 0.15) +
            (playability_score * 0.10)
        )
        return round(composite, 1)

    async def get_recommendations(self, profile: EmotionalProfile, query: str = None) -> List[Track]:
        # music provider interface hasn't changed, pass it what it needs
        # We can simulate the old MoodProfile for the provider's fetch step since it just uses the top genre
        class MockMoodForProvider:
            genres = [gw.genre for gw in profile.weighted_genres]
            tempo = profile.tempo
        
        candidates = await self.music_provider.fetch_candidates(MockMoodForProvider(), query=query)
        
        if not candidates:
            return []

        # Calculate scores and sort descending
        scored_tracks: List[Track] = []
        for track in candidates:
            score = self._score_track(track, profile)
            track.matchScore = score
            scored_tracks.append(track)
            
        scored_tracks.sort(key=lambda t: t.matchScore, reverse=True)
        
        # Select top 5 tracks max
        return scored_tracks[:5]
