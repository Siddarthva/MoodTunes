import json
import numpy as np
from pathlib import Path
from app.providers.emotion.base import BaseEmotionProvider
from app.schemas.analyze import EmotionResult, EmotionProbabilities
from app.core.exceptions import ModelNotReadyException

# Absolute path to the models/emotion directory, anchored at this file's location.
# This file lives at: backend/app/providers/emotion/moodtunes_cnn.py
# So: __file__ -> .../providers/emotion/ -> up 3 -> backend/ -> app/models/emotion/
_PROVIDER_DIR = Path(__file__).resolve().parent          # .../providers/emotion/
_BACKEND_DIR  = _PROVIDER_DIR.parent.parent.parent       # .../backend/
_EMOTION_MODEL_DIR = _BACKEND_DIR / "app" / "models" / "emotion"


class MoodTunesCNNProvider(BaseEmotionProvider):
    """
    Keras CNN Emotion Provider for FER2013 7-class classifier.
    Loads moodtunes_emotion_cnn.keras and emotion_labels.json using absolute
    paths anchored to __file__, so the model is found regardless of the process
    working directory.
    """

    def __init__(self, model_path: str, labels_path: str = None):
        # Always resolve to an absolute path using pathlib, falling back to the
        # canonical model directory if the caller passed a relative hint.
        model_p = Path(model_path)
        if not model_p.is_absolute():
            model_p = (_BACKEND_DIR / model_path).resolve()

        # If the resolved path still doesn't exist, try the canonical location.
        if not model_p.exists():
            canonical = _EMOTION_MODEL_DIR / "moodtunes_emotion_cnn.keras"
            if canonical.exists():
                model_p = canonical

        self.model_path = str(model_p)

        # Resolve labels path the same way.
        if labels_path:
            labels_p = Path(labels_path)
            if not labels_p.is_absolute():
                labels_p = (_BACKEND_DIR / labels_path).resolve()
        else:
            labels_p = _EMOTION_MODEL_DIR / "emotion_labels.json"

        self.labels_path = str(labels_p)

        self.model = None
        self.labels_map = {}
        self._load_labels()
        self._load_model()

    def _load_labels(self):
        labels_p = Path(self.labels_path)
        if not labels_p.exists():
            self.labels_map = {
                0: "angry", 1: "disgust", 2: "fear", 3: "happy",
                4: "sad", 5: "surprise", 6: "neutral"
            }
            return

        try:
            with open(labels_p, "r", encoding="utf-8") as f:
                data = json.load(f)
            if isinstance(data, dict):
                self.labels_map = {int(k): str(v).lower() for k, v in data.items()}
            elif isinstance(data, list):
                self.labels_map = {idx: str(v).lower() for idx, v in enumerate(data)}

            if len(self.labels_map) != 7:
                raise ValueError(
                    f"Expected 7 classes in labels file, got {len(self.labels_map)}"
                )
        except Exception:
            self.labels_map = {
                0: "angry", 1: "disgust", 2: "fear", 3: "happy",
                4: "sad", 5: "surprise", 6: "neutral"
            }

    def _load_model(self):
        model_p = Path(self.model_path)
        if not model_p.exists():
            raise ModelNotReadyException(
                f"Keras model artifact not found at '{self.model_path}'. "
                "Place 'moodtunes_emotion_cnn.keras' into "
                "'backend/app/models/emotion/' and restart the server."
            )

        try:
            import tensorflow as tf  # deferred import keeps startup fast when mock is used
            self.model = tf.keras.models.load_model(str(model_p))
        except Exception as e:
            raise ModelNotReadyException(f"Failed to load Keras model: {e}")

        # Verify tensor contract: input (None,48,48,1), output (None,7)
        in_shape = tuple(self.model.input_shape)
        out_shape = tuple(self.model.output_shape)
        if in_shape != (None, 48, 48, 1):
            raise ModelNotReadyException(
                f"Unexpected model input shape {in_shape}. Expected (None, 48, 48, 1)."
            )
        if out_shape[-1] != 7:
            raise ModelNotReadyException(
                f"Unexpected model output classes {out_shape[-1]}. Expected 7."
            )

        print(
            f"[MoodTunesCNN] Model loaded OK | path={model_p.name} "
            f"| input={in_shape} | output={out_shape}"
        )

    def predict(self, face_tensor: np.ndarray) -> EmotionResult:
        if self.model is None:
            raise ModelNotReadyException("MoodTunes CNN model is not initialized.")

        # face_tensor shape: (1, 48, 48, 1) float32 in [0, 1]
        raw_predictions = self.model.predict(face_tensor, verbose=0)[0]

        probabilities_dict: dict[str, float] = {}
        for idx, default_label in enumerate(self.EMOTION_LABELS):
            label_name = self.labels_map.get(idx, default_label)
            prob = float(raw_predictions[idx]) * 100.0 if idx < len(raw_predictions) else 0.0
            probabilities_dict[label_name] = round(prob, 1)

        top_idx = int(np.argmax(raw_predictions))
        top_label = self.labels_map.get(top_idx, "neutral")
        confidence = probabilities_dict.get(top_label, 0.0)

        probs_schema = EmotionProbabilities(**probabilities_dict)

        return EmotionResult(
            dominant=top_label,
            confidence=confidence,
            probabilities=probs_schema,
        )
