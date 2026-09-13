import numpy as np
import random
from app.providers.emotion.base import BaseEmotionProvider
from app.schemas.analyze import EmotionResult, EmotionProbabilities

class MockEmotionProvider(BaseEmotionProvider):
    """
    Mock provider for development/testing when the real CNN model is not yet trained.
    Returns deterministic or randomized emotion probabilities adhering strictly to the contract.
    """
    def __init__(self, default_emotion: str = "happy"):
        self.default_emotion = default_emotion if default_emotion in self.EMOTION_LABELS else "happy"

    def predict(self, face_tensor: np.ndarray) -> EmotionResult:
        # Generate base probability distribution
        raw_probs = {}
        for label in self.EMOTION_LABELS:
            if label == self.default_emotion:
                raw_probs[label] = random.uniform(75.0, 92.0)
            else:
                raw_probs[label] = random.uniform(0.5, 5.0)
                
        # Normalize sum to 100.0%
        total = sum(raw_probs.values())
        normalized_probs = {k: round((v / total) * 100.0, 1) for k, v in raw_probs.items()}
        
        # Ensure highest probability matches top emotion label
        top_label = max(normalized_probs, key=normalized_probs.get)
        confidence = normalized_probs[top_label]
        
        probs_schema = EmotionProbabilities(**normalized_probs)
        
        return EmotionResult(
            dominant=top_label,
            confidence=confidence,
            probabilities=probs_schema
        )
