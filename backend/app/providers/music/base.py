from abc import ABC, abstractmethod
from typing import List, Any
from app.schemas.analyze import Track

class BaseMusicProvider(ABC):
    @abstractmethod
    async def fetch_candidates(self, mood: Any, query: str = None) -> List[Track]:
        """
        Fetches candidate tracks for a given mood profile or query.
        """
        pass
