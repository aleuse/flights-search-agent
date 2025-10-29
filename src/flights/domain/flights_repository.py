"""Repository interface for flight data operations."""
from abc import ABC, abstractmethod
from typing import List
from flights.domain.flights_entities import FlightSearchRequest, Flight

class FlightRepository(ABC):
  """Abstract repository for flight search operations."""
  @abstractmethod
  async def search_flights(self, request: FlightSearchRequest) -> List[Flight]:
    pass