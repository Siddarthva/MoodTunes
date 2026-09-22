from typing import List
from app.schemas.analyze import Track, EmotionalProfile
from app.schemas.music import GroqMusicDirection
from app.providers.music.base import BaseMusicProvider

class RecommendationService:
    """
    Ranks candidate tracks using composite weighted scoring based on emotional profile alignment,
    genre matching, and audio preview playability. Applies deduplication and artist diversity logic.
    """
    def __init__(self, music_provider: BaseMusicProvider):
        self.music_provider = music_provider

    def _score_track(self, track: Track, profile: EmotionalProfile) -> float:
        # 1. Emotion Profile Match Score (30%)
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
        playability_score = 100.0 if track.playable else (100.0 if track.previewUrl else 0.0)
        
        composite = (
            (profile_match_score * 0.30) +
            (genre_score * 0.25) +
            (energy_score * 0.20) +
            (valence_score * 0.15) +
            (playability_score * 0.10)
        )
        return round(composite, 1)

    async def get_recommendations(self, profile: EmotionalProfile, direction: GroqMusicDirection = None, query: str = None) -> List[Track]:
        candidates = await self.music_provider.fetch_candidates(mood=profile, direction=direction, query=query)
        
        if not candidates:
            return []

        # 1. Deduplicate candidates (Title + Artist)
        unique_tracks = {}
        for track in candidates:
            key = f"{track.title.lower().strip()}_{track.artist.lower().strip()}"
            if key not in unique_tracks:
                unique_tracks[key] = track
            else:
                # If duplicate exists, keep the playable one
                if track.playable and not unique_tracks[key].playable:
                    unique_tracks[key] = track

        # 2. Score tracks
        scored_tracks: List[Track] = []
        for track in unique_tracks.values():
            # Calculate individual components to determine reason
            profile_match_score = 0.0
            for gw in profile.weighted_genres:
                if gw.genre.lower() in track.genre.lower():
                    profile_match_score += gw.weight
            
            top_genre = profile.weighted_genres[0].genre.lower() if profile.weighted_genres else ""
            genre_score = 95.0 if top_genre in track.genre.lower() else 75.0
            
            # Determine reason
            reason = "Fits the shape of the moment."
            if profile_match_score > 50:
                reason = "Aligns strongly with your emotional profile."
            elif genre_score > 90:
                reason = f"Matches the {top_genre.capitalize() if top_genre else 'mood'} energy."
            elif profile.energy > 70:
                reason = "Matches your current high energy."
            elif profile.energy < 40:
                reason = "Balances the calmer part of your profile."
            elif profile.valence > 70:
                reason = "Fits the positive side of your mood."
            else:
                reason = "Adds a different texture to the mix."

            track.source_metadata["why_this_fits"] = reason
            track.matchScore = self._score_track(track, profile)
            scored_tracks.append(track)
            
        # 3. Sort descending by score
        scored_tracks.sort(key=lambda t: t.matchScore, reverse=True)
        
        # 4. Select top 5 tracks with artist diversity constraint (max 2 per artist)
        final_selection = []
        artist_counts = {}
        
        for track in scored_tracks:
            if len(final_selection) >= 5:
                break
                
            artist_key = track.artist.lower().strip()
            count = artist_counts.get(artist_key, 0)
            
            if count < 2:
                final_selection.append(track)
                artist_counts[artist_key] = count + 1
                
        # If we couldn't get 5 tracks due to diversity constraints but have more tracks, just fill it up
        if len(final_selection) < 5:
            for track in scored_tracks:
                if len(final_selection) >= 5:
                    break
                if track not in final_selection:
                    final_selection.append(track)

        return final_selection
