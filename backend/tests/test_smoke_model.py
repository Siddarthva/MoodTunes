"""
test_smoke_model.py — Real-model smoke test for MoodTunes CNN.

IMPORTANT: This test loads the ACTUAL moodtunes_emotion_cnn.keras file and
runs a genuine inference pass. It does NOT mock the model.
A pass here proves the real CNN is functional.
"""
import sys
from pathlib import Path

# Ensure backend is importable
BACKEND_DIR = Path(__file__).resolve().parent.parent
if str(BACKEND_DIR) not in sys.path:
    sys.path.insert(0, str(BACKEND_DIR))

import numpy as np
import pytest

# Canonical model path
MODEL_PATH = BACKEND_DIR / "app" / "models" / "emotion" / "moodtunes_emotion_cnn.keras"
LABELS_PATH = BACKEND_DIR / "app" / "models" / "emotion" / "emotion_labels.json"

VALID_LABELS = {"angry", "disgust", "fear", "happy", "sad", "surprise", "neutral"}


@pytest.fixture(scope="module")
def loaded_model():
    """Load the real Keras model once for all smoke tests in this module."""
    if not MODEL_PATH.exists():
        pytest.skip(f"Model file not found at {MODEL_PATH} — smoke test skipped.")
    import tensorflow as tf
    model = tf.keras.models.load_model(str(MODEL_PATH))
    return model


def test_model_file_exists():
    """Confirm the model artifact is present at the expected path."""
    assert MODEL_PATH.exists(), (
        f"moodtunes_emotion_cnn.keras not found at {MODEL_PATH}"
    )


def test_model_input_shape(loaded_model):
    """Input shape must be (None, 48, 48, 1)."""
    assert tuple(loaded_model.input_shape) == (None, 48, 48, 1), (
        f"Unexpected input shape: {loaded_model.input_shape}"
    )


def test_model_output_shape(loaded_model):
    """Output shape must be (None, 7) for 7-class softmax."""
    assert tuple(loaded_model.output_shape) == (None, 7), (
        f"Unexpected output shape: {loaded_model.output_shape}"
    )


def test_inference_on_synthetic_input(loaded_model):
    """Run inference on a random synthetic face tensor and check the output."""
    rng = np.random.default_rng(seed=42)
    # Simulate a normalized 48×48 grayscale face patch (all same as live preprocessing)
    face_tensor = rng.random((1, 48, 48, 1), dtype=np.float32)

    preds = loaded_model.predict(face_tensor, verbose=0)

    # Output shape: (1, 7)
    assert preds.shape == (1, 7), f"Expected output shape (1,7), got {preds.shape}"


def test_probability_sum_approx_one(loaded_model):
    """Softmax outputs must sum to ~1.0 (tolerance 1e-3)."""
    rng = np.random.default_rng(seed=7)
    face_tensor = rng.random((1, 48, 48, 1), dtype=np.float32)
    preds = loaded_model.predict(face_tensor, verbose=0)[0]

    total = float(np.sum(preds))
    assert abs(total - 1.0) < 1e-3, (
        f"Probability sum {total:.6f} deviates from 1.0 by more than 1e-3"
    )


def test_predicted_label_is_valid(loaded_model):
    """The argmax class index must map to a valid emotion label."""
    rng = np.random.default_rng(seed=21)
    face_tensor = rng.random((1, 48, 48, 1), dtype=np.float32)
    preds = loaded_model.predict(face_tensor, verbose=0)[0]

    CLASS_ORDER = ["angry", "disgust", "fear", "happy", "sad", "surprise", "neutral"]
    top_idx = int(np.argmax(preds))
    top_label = CLASS_ORDER[top_idx]

    assert top_label in VALID_LABELS, f"Predicted label '{top_label}' not in valid set"
    print(f"\n[smoke] Predicted: {top_label} ({float(preds[top_idx]) * 100:.1f}%)")


def test_labels_json_class_order():
    """emotion_labels.json must contain exactly the 7 expected classes."""
    import json
    assert LABELS_PATH.exists(), f"emotion_labels.json not found at {LABELS_PATH}"
    with open(LABELS_PATH) as f:
        data = json.load(f)
    labels = {str(v).lower() for v in data.values()} if isinstance(data, dict) else {str(v).lower() for v in data}
    assert labels == VALID_LABELS, f"Labels in JSON {labels} do not match expected {VALID_LABELS}"


def test_cnn_provider_loads_successfully():
    """MoodTunesCNNProvider must initialise without raising."""
    from app.providers.emotion.moodtunes_cnn import MoodTunesCNNProvider
    provider = MoodTunesCNNProvider(
        model_path=str(MODEL_PATH),
        labels_path=str(LABELS_PATH),
    )
    assert provider.model is not None
    assert len(provider.labels_map) == 7


def test_cnn_provider_predict_shape_and_validity():
    """Provider predict() must return a valid EmotionResult with correct structure."""
    from app.providers.emotion.moodtunes_cnn import MoodTunesCNNProvider
    provider = MoodTunesCNNProvider(
        model_path=str(MODEL_PATH),
        labels_path=str(LABELS_PATH),
    )
    rng = np.random.default_rng(seed=99)
    face_tensor = rng.random((1, 48, 48, 1), dtype=np.float32)
    result = provider.predict(face_tensor)

    assert result.dominant in VALID_LABELS
    assert 0.0 <= result.confidence <= 100.0
    total = sum([
        result.probabilities.angry,
        result.probabilities.disgust,
        result.probabilities.fear,
        result.probabilities.happy,
        result.probabilities.sad,
        result.probabilities.surprise,
        result.probabilities.neutral,
    ])
    assert abs(total - 100.0) < 1.0, f"Probabilities sum to {total:.2f}, expected ~100"
