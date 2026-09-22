from typing import Dict, List
from collections import defaultdict
from app.schemas.analyze import EmotionalProfile, GenreWeight
from app.core.exceptions import MoodTunesException

class MoodService:
    """
    Maps the 7-class emotion probability distribution to a weighted emotional profile.
    """
    # Base characteristics for each emotion
    MOOD_MAPPINGS = {
        "happy": {"energy": 85, "valence": 90, "genres": ["Pop", "Dance", "Feel Good"]},
        "sad": {"energy": 30, "valence": 30, "genres": ["Lo-Fi", "Acoustic", "Indie"]},
        "angry": {"energy": 90, "valence": 35, "genres": ["Rock", "Hip-Hop", "Metal"]},
        "neutral": {"energy": 50, "valence": 55, "genres": ["Lo-Fi", "Chill", "Ambient"]},
        "surprise": {"energy": 80, "valence": 75, "genres": ["Pop", "Electronic", "Dance"]},
        "fear": {"energy": 25, "valence": 50, "genres": ["Ambient", "Classical", "Lo-Fi"]},
        "disgust": {"energy": 65, "valence": 35, "genres": ["Alternative", "Rock", "Hip-Hop"]}
    }

    MEANINGFUL_THRESHOLD = 5.0  # 5% minimum probability to influence recommendations

    @classmethod
    def calculate_emotional_profile(cls, dominant_emotion: str, probabilities: dict) -> EmotionalProfile:
        total_weight = 0.0
        weighted_energy = 0.0
        weighted_valence = 0.0
        genre_scores: Dict[str, float] = defaultdict(float)

        # 1. Filter meaningful emotions and calculate total valid weight
        valid_emotions = {}
        for emotion, prob in probabilities.items():
            if prob >= cls.MEANINGFUL_THRESHOLD:
                valid_emotions[emotion] = prob
                total_weight += prob

        # Fallback to dominant emotion if everything was somehow below threshold
        if total_weight == 0:
            valid_emotions = {dominant_emotion: 100.0}
            total_weight = 100.0

        # 2. Calculate normalized weighted averages
        for emotion, prob in valid_emotions.items():
            # Normalized weight for this emotion (so they sum to 1.0)
            norm_weight = prob / total_weight
            
            base_traits = cls.MOOD_MAPPINGS.get(emotion.lower(), cls.MOOD_MAPPINGS["neutral"])
            
            weighted_energy += base_traits["energy"] * norm_weight
            weighted_valence += base_traits["valence"] * norm_weight
            
            # Distribute the unnormalized probability weight across genres
            for genre in base_traits["genres"]:
                genre_scores[genre] += prob

        # 3. Determine tempo based on aggregate energy
        if weighted_energy > 70:
            tempo = "high"
        elif weighted_energy < 40:
            tempo = "low"
        else:
            tempo = "medium"

        # 4. Format and sort genre weights
        weighted_genres = [
            GenreWeight(genre=g, weight=round(w, 1))
            for g, w in genre_scores.items()
        ]
        weighted_genres.sort(key=lambda x: x.weight, reverse=True)

        return EmotionalProfile(
            dominant_emotion=dominant_emotion,
            energy=round(weighted_energy, 1),
            valence=round(weighted_valence, 1),
            tempo=tempo,
            weighted_genres=weighted_genres
        )

    @classmethod
    def get_mood_for_emotion(cls, dominant_emotion: str = "neutral") -> EmotionalProfile:
        emotion = (dominant_emotion.lower() if dominant_emotion else "neutral").strip()
        if emotion not in cls.MOOD_MAPPINGS:
            emotion = "neutral"
        probabilities = {e: (100.0 if e == emotion else 0.0) for e in cls.MOOD_MAPPINGS.keys()}
        return cls.calculate_emotional_profile(dominant_emotion=emotion, probabilities=probabilities)

