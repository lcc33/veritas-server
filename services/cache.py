from models.schemas import AnalysisResponse
from typing import Optional

class AnalysisCache:
    def __init__(self):
        self._cache = {}
    
    async def get_cached_analysis(self, key: str) -> Optional[AnalysisResponse]:
        """Mock cache get"""
        return self._cache.get(key)
    
    async def set_cached_analysis(self, key: str, result: AnalysisResponse):
        """Mock cache set"""
        self._cache[key] = result