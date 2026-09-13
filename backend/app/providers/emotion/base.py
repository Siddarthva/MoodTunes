from abc import ABC, abstractmethod
import numpy as np
from app.schemas.analyze import EmotionResult, EmotionProbabilities

class BaseEmotionProvider(ABC):
    EMOTION_LABELS = ["angry", "disgust", "fear", "happy", "sad", "surprise", "neutral"]

    @abstractmethod
    def predict(self, face_tensor: np.ndarray) -> EmotionResult:
        """
        Takes a (1, 48, 48, 1) float32 tensor [0..1] and returns an EmotionResult.
        """
        pass
