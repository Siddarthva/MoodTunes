from fastapi.testclient import TestClient
import numpy as np
import pytest
import cv2
from unittest.mock import AsyncMock

from app.main import app
from app.providers.emotion.mock import MockEmotionProvider
from app.providers.emotion.moodtunes_cnn import MoodTunesCNNProvider
from app.services.mood_service import MoodService
from app.services.recommendation_service import RecommendationService
from app.providers.music.itunes import ITunesMusicProvider
from app.vision.face_detector import FaceDetector
from app.schemas.analyze import EmotionalProfile, Track, GenreWeight
from app.core.config import settings

client = TestClient(app)

def test_health_endpoint():
    response = client.get("/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "ok"
    assert data["project"] == "MoodTunes API"
    assert "model" in data
    assert "loaded" in data["model"]
    assert "provider" in data["model"]

def test_analyze_no_file():
    response = client.post("/api/analyze")
    assert response.status_code in [400, 422]

def test_analyze_empty_file():
    files = {"image": ("empty.jpg", b"", "image/jpeg")}
    response = client.post("/api/analyze", files=files)
    assert response.status_code == 422
    data = response.json()
    assert data["success"] is False
    assert data["error"]["code"] in ["CORRUPT_IMAGE", "INVALID_PAYLOAD"]

def test_analyze_corrupt_image_when_mock_active():
    with TestClient(app) as test_client:
        test_client.app.state.face_detector = FaceDetector(cascade_path=settings.HAAR_CASCADE_PATH)
        test_client.app.state.emotion_provider = MockEmotionProvider()
        test_client.app.state.model_loaded = True
        
        files = {"image": ("bad.jpg", b"invalid_bytes_data", "image/jpeg")}
        response = test_client.post("/api/analyze", files=files)
        assert response.status_code == 422
        data = response.json()
        assert data["success"] is False
        assert data["error"]["code"] == "CORRUPT_IMAGE"

def test_analyze_no_face_image():
    # Synthetic image with no face (blank gray image)
    img = np.zeros((200, 200, 3), dtype=np.uint8)
    _, img_encoded = cv2.imencode(".jpg", img)
    
    with TestClient(app) as test_client:
        test_client.app.state.face_detector = FaceDetector(cascade_path=settings.HAAR_CASCADE_PATH)
        test_client.app.state.emotion_provider = MockEmotionProvider()
        test_client.app.state.model_loaded = True
        
        files = {"image": ("noface.jpg", img_encoded.tobytes(), "image/jpeg")}
        response = test_client.post("/api/analyze", files=files)
        assert response.status_code == 422
        data = response.json()
        assert data["success"] is False
        assert data["error"]["code"] == "NO_FACE_DETECTED"

def test_mock_emotion_provider():
    provider = MockEmotionProvider(default_emotion="happy")
    dummy_tensor = np.zeros((1, 48, 48, 1), dtype=np.float32)
    result = provider.predict(dummy_tensor)
    assert result.dominant in provider.EMOTION_LABELS
    assert result.confidence > 0
    assert result.probabilities.happy > 0

def test_mood_service_mapping():
    probs = {"happy": 80.0, "surprise": 20.0}
    profile = MoodService.calculate_emotional_profile("happy", probs)
    assert profile.dominant_emotion == "happy"
    assert profile.energy > 50
    assert profile.valence > 50
    assert profile.tempo == "high"
    assert len(profile.weighted_genres) > 0
    # Pop should have weight from both happy and surprise
    assert any(g.genre == "Pop" for g in profile.weighted_genres)

def test_recommendation_scoring():
    # Mock network call for ITunesMusicProvider in unit test
    mock_provider = ITunesMusicProvider()
    mock_provider.fetch_candidates = AsyncMock(return_value=[])
    
    service = RecommendationService(music_provider=mock_provider)
    profile = EmotionalProfile(
        dominant_emotion="happy",
        energy=85.0,
        valence=90.0,
        tempo="high",
        weighted_genres=[GenreWeight(genre="Pop", weight=100.0)]
    )
    sample_track = Track(
        id="test_1",
        title="Test Track",
        artist="Test Artist",
        album="Test Album",
        genre="Pop",
        artworkUrl="http://example.com/art.jpg",
        previewUrl="http://example.com/preview.mp3",
        source="iTunes",
        matchScore=0.0
    )
    score = service._score_track(sample_track, profile)
    assert score > 50.0

def test_model_missing_behavior():
    """Provider must raise if the model file does not exist and canonical fallback is also absent."""
    from unittest.mock import patch
    from pathlib import Path
    import app.providers.emotion.moodtunes_cnn as cnn_module

    # Temporarily override the canonical emotion model dir to a non-existent location
    # so neither the caller-provided path nor the fallback resolves.
    fake_dir = Path("/non_existent_xyz_dir")
    with patch.object(cnn_module, "_EMOTION_MODEL_DIR", fake_dir):
        with pytest.raises(Exception):
            MoodTunesCNNProvider(
                model_path="/non_existent_xyz_dir/fake_model.keras",
                labels_path="/non_existent_xyz_dir/fake_labels.json",
            )


def test_analyze_with_mock_provider():
    with TestClient(app) as test_client:
        test_client.app.state.emotion_provider = MockEmotionProvider()
        test_client.app.state.model_loaded = True

        health_resp = test_client.get("/health")
        assert health_resp.json()["model"]["loaded"] is True


# ---------------------------------------------------------------------------
# Additional contract tests
# ---------------------------------------------------------------------------

def test_probability_sum():
    """Probabilities returned by mock provider must sum to ~100."""
    provider = MockEmotionProvider(default_emotion="neutral")
    dummy = np.zeros((1, 48, 48, 1), dtype=np.float32)
    result = provider.predict(dummy)
    total = (
        result.probabilities.angry
        + result.probabilities.disgust
        + result.probabilities.fear
        + result.probabilities.happy
        + result.probabilities.sad
        + result.probabilities.surprise
        + result.probabilities.neutral
    )
    assert abs(total - 100.0) < 2.0, f"Probability sum {total:.2f} is not ~100"


def test_emotion_label_validity():
    """Provider predict() must return a label from the canonical 7-class set."""
    valid_labels = {"angry", "disgust", "fear", "happy", "sad", "surprise", "neutral"}
    for emotion in valid_labels:
        provider = MockEmotionProvider(default_emotion=emotion)
        dummy = np.zeros((1, 48, 48, 1), dtype=np.float32)
        result = provider.predict(dummy)
        assert result.dominant in valid_labels, (
            f"Returned label '{result.dominant}' is not in the valid set"
        )


def test_recommendation_limit():
    """RecommendationService must never return more than 5 tracks."""
    from app.schemas.analyze import Track, EmotionalProfile, GenreWeight

    mock_provider = ITunesMusicProvider()
    # Supply 10 fake tracks — service must trim to 5
    fake_tracks = [
        Track(
            id=f"t_{i}",
            title=f"Track {i}",
            artist="Artist",
            album="Album",
            genre="Pop",
            artworkUrl="http://example.com/art.jpg",
            previewUrl="http://example.com/preview.mp3",
            source="iTunes",
            matchScore=0.0,
        )
        for i in range(10)
    ]
    mock_provider.fetch_candidates = AsyncMock(return_value=fake_tracks)

    import asyncio
    service = RecommendationService(music_provider=mock_provider)
    profile = EmotionalProfile(
        dominant_emotion="happy",
        energy=85.0,
        valence=90.0,
        tempo="high",
        weighted_genres=[GenreWeight(genre="Pop", weight=100.0)]
    )
    results = asyncio.run(service.get_recommendations(profile=profile))
    assert len(results) <= 5, f"Expected ≤ 5 recommendations, got {len(results)}"
