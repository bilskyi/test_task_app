import httpx
from typing import Optional, Dict
from datetime import datetime, timedelta

class ArtInstituteService:
    BASE_URL = "https://api.artic.edu/api/v1"
    CACHE_TTL = timedelta(hours=1)
    
    def __init__(self):
        self._cache: Dict[int, tuple[dict, datetime]] = {}
    
    def _is_cache_valid(self, cache_time: datetime) -> bool:
        """Check if cached data is still valid"""
        return datetime.now() - cache_time < self.CACHE_TTL
    
    async def get_artwork(self, artwork_id: int) -> Optional[dict]:
        """
        Fetch artwork details from Art Institute API with caching
        
        Args:
            artwork_id: The external ID of the artwork
            
        Returns:
            Dictionary with artwork data or None if not found
        """
        # Check cache first
        if artwork_id in self._cache:
            cached_data, cache_time = self._cache[artwork_id]
            if self._is_cache_valid(cache_time):
                return cached_data
        
 
        url = f"{self.BASE_URL}/artworks/{artwork_id}"
        
        try:
            async with httpx.AsyncClient() as client:
                response = await client.get(url, timeout=10.0)
                
                if response.status_code == 200:
                    data = response.json()
                    artwork_data = data.get("data", {})
                    
                    result = {
                        "id": int(artwork_data.get("id", artwork_id)),
                        "title": artwork_data.get("title", "Unknown")
                    }
                    self._cache[artwork_id] = (result, datetime.now())
                    
                    return result
                elif response.status_code == 404:
                    return None
                else:
                    return None
                    
        except httpx.RequestError:
            return None
        except Exception:
            return None
    
    async def validate_artwork_exists(self, artwork_id: int) -> bool:
        """
        Validate that an artwork exists in the API
        
        Args:
            artwork_id: The external ID to validate
            
        Returns:
            True if artwork exists, False otherwise
        """
        artwork = await self.get_artwork(artwork_id)
        return artwork is not None


art_service = ArtInstituteService()