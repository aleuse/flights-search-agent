"""Repository implementation for location searches using Amadeus API."""
from typing import List
from amadeus.infrastructure.amadeus_client import AmadeusClient
from locations.domain.location_repository import LocationRepository
from locations.domain.location_entities import LocationSearchRequest, Location
from shared.logging import setup_logger, log_function_call, log_function_result, log_function_error

class SearchLocationsRepository(LocationRepository):
  """Repository implementation for searching locations via Amadeus API."""
  def __init__(self, client: AmadeusClient):
    """Initialize the location search repository.
    
    Args:
      client: Amadeus API client instance
    """
    self.client = client
    self.logger = setup_logger("search_locations_repository")
    
  async def search_locations(self, request: LocationSearchRequest) -> List[Location]:
    """Search for locations using the Amadeus API.
    
    Args:
      request: Location search request with city name
      
    Returns:
      List of location objects matching the city name
      
    Raises:
      Exception: If search fails
    """
    log_function_call(self.logger, "search_locations", {
      "city": request.city
    })
    try:
      raw_data = self.client.search_locations(request.city)
      locations = self._parse_locations(raw_data)
      log_function_result(self.logger, "search_locations", {"locations_count": len(locations)})
      return locations
    except Exception as e:
      log_function_error(self.logger, "search_locations", e, {
        "city": request.city
      })
      raise
      
  def _parse_locations(self, raw_data: dict) -> List[Location]:
    """Parse raw location data from Amadeus API into domain entities.
    
    Args:
      raw_data: Raw location data from API response
      
    Returns:
      List of Location domain entities
    """
    locations = []
    if isinstance(raw_data, dict) and "data" in raw_data:
      for location in raw_data["data"]:
        locations.append(Location(
          name=location["name"],
          iata_code=location["iataCode"],
          country=location["address"]["countryCode"]
        ))
    return locations