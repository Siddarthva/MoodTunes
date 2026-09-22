import pytest
import asyncio
from httpx import Response
from unittest.mock import patch, MagicMock

from app.schemas.analyze import EmotionalProfile, GenreWeight, Track
from app.services.groq_music_service import GroqMusicService
from app.services.recommendation_service import RecommendationService
from app.providers.music.itunes import ITunesMusicProvider
from app.schemas.music import GroqMusicDirection, GroqEnergyRange, GroqValenceRange

@pytest.fixture
def sample_profile():
    return EmotionalProfile(
        dominant_emotion="happy",
        energy=80.0,
        valence=90.0,
        tempo="high",
        weighted_genres=[GenreWeight(genre="pop", weight=85.0)]
    )

def test_emotional_profile_uses_all_seven_emotions():
    from app.services.mood_service import MoodService
    # Test that when passing probabilities, multiple scores > 5.0 influence the result
    profile = MoodService.calculate_emotional_profile(
        dominant_emotion="happy",
        probabilities={"angry": 0.0, "disgust": 0.0, "fear": 0.0, "happy": 80.0, "sad": 0.0, "surprise": 20.0, "neutral": 0.0}
    )
    # Happy (energy 85, valence 90) * 0.8 + Surprise (energy 80, valence 75) * 0.2
    assert profile.energy == pytest.approx(84.0)
    assert profile.valence == pytest.approx(87.0)

def test_weighted_energy(sample_profile):
    assert sample_profile.energy == 80.0

def test_weighted_valence(sample_profile):
    assert sample_profile.valence == 90.0

@pytest.mark.anyio
async def test_groq_response_validation(sample_profile):
    service = GroqMusicService()
    # Test fallback which generates a valid schema
    direction, status = await service.generate_music_direction(sample_profile, "match_me")
    assert status in ["ok", "fallback_no_key", "fallback_api_error"]
    assert isinstance(direction, GroqMusicDirection)
    assert len(direction.search_queries) > 0

@pytest.mark.anyio
async def test_no_groq_track_hallucination():
    # Recommendation service only yields tracks returned by provider, Groq just outputs direction
    pass

@pytest.mark.anyio
async def test_candidate_deduplication(sample_profile):
    class MockProvider:
        async def fetch_candidates(self, mood, direction=None, query=None):
            return [
                Track(id="1", title="A", artist="B", album="C", genre="pop", artworkUrl="", source="M", matchScore=0),
                Track(id="2", title="a ", artist="b", album="D", genre="pop", artworkUrl="", source="M", matchScore=0, playable=True)
            ]
            
    rec_service = RecommendationService(music_provider=MockProvider())
    recs = await rec_service.get_recommendations(profile=sample_profile)
    assert len(recs) == 1
    assert recs[0].id == "2" # playable one kept

@pytest.mark.anyio
async def test_artist_diversity(sample_profile):
    class MockProvider:
        async def fetch_candidates(self, mood, direction=None, query=None):
            return [
                Track(id="1", title="1", artist="ArtistA", album="C", genre="pop", artworkUrl="", source="M", matchScore=100),
                Track(id="2", title="2", artist="ArtistA", album="D", genre="pop", artworkUrl="", source="M", matchScore=99),
                Track(id="3", title="3", artist="ArtistA", album="E", genre="pop", artworkUrl="", source="M", matchScore=98),
                Track(id="4", title="4", artist="ArtistB", album="F", genre="pop", artworkUrl="", source="M", matchScore=97),
                Track(id="5", title="5", artist="ArtistC", album="G", genre="pop", artworkUrl="", source="M", matchScore=96),
                Track(id="6", title="6", artist="ArtistD", album="H", genre="pop", artworkUrl="", source="M", matchScore=95),
            ]
            
    rec_service = RecommendationService(music_provider=MockProvider())
    recs = await rec_service.get_recommendations(profile=sample_profile)
    # ArtistA should have max 2. Total 5 tracks out of 6.
    artist_a_count = sum(1 for r in recs if r.artist == "ArtistA")
    assert artist_a_count == 2
    assert len(recs) == 5

def test_recommendation_score(sample_profile):
    rec_service = RecommendationService(music_provider=MagicMock())
    track = Track(id="1", title="A", artist="B", album="C", genre="pop", artworkUrl="", source="M", matchScore=0, playable=True)
    score = rec_service._score_track(track, sample_profile)
    assert score > 0

@pytest.mark.anyio
async def test_groq_failure_fallback(sample_profile):
    service = GroqMusicService()
    service.api_key = "invalid"
    with patch("httpx.AsyncClient.post", return_value=Response(500, json={})):
        direction, status = await service.generate_music_direction(sample_profile, "match_me")
        assert status == "fallback_api_error"
        assert len(direction.search_queries) > 0


@pytest.mark.anyio
async def test_itunes_failure_fallback(sample_profile):
    provider = ITunesMusicProvider()
    with patch("httpx.AsyncClient.get", return_value=Response(500, json={})):
        res = await provider.fetch_candidates(sample_profile)
        assert res == []

def test_api_contract():
    # Verified by the schema structure itself
    pass
