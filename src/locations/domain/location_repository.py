"""Repository interface for location data operations."""
from abc import ABC, abstractmethod
from typing import List
from locations.domain.location_entities import LocationSearchRequest, Location

class LocationRepository(ABC):
  """Abstract repository for location search operations."""
  @abstractmethod
  async def search_locations(self, request: LocationSearchRequest) -> List[Location]:
      pass