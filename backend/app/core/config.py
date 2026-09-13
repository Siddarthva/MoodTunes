from pydantic_settings import BaseSettings, SettingsConfigDict
from typing import List, Union
from pydantic import field_validator

class Settings(BaseSettings):
    PROJECT_NAME: str = "MoodTunes API"
    DEBUG: bool = True

    CORS_ORIGINS: List[str] = [
        "http://localhost:5173",
        "http://127.0.0.1:5173",
        "http://localhost:5174",
        "http://127.0.0.1:5174",
        "http://localhost:3000",
    ]

    EMOTION_PROVIDER: str = "moodtunes_cnn"  # moodtunes_cnn | mock
    EMOTION_MODEL_PATH: str = "app/models/emotion/moodtunes_emotion_cnn.keras"
    EMOTION_LABELS_PATH: str = "app/models/emotion/emotion_labels.json"
    HAAR_CASCADE_PATH: str = "app/models/haarcascade_frontalface_default.xml"

    MUSIC_PROVIDER: str = "jamendo"  # jamendo | itunes
    JAMENDO_CLIENT_ID: str = ""
    ITUNES_ENABLED: bool = True

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore"
    )

    @field_validator("CORS_ORIGINS", mode="before")
    @classmethod
    def parse_cors_origins(cls, v: Union[str, List[str]]) -> List[str]:
        if isinstance(v, str):
            return [i.strip() for i in v.split(",")]
        return v

settings = Settings()

