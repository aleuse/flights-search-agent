"""Application use case for searching locations."""
from typing import List
from locations.domain.location_repository import LocationRepository
from locations.domain.location_entities import LocationSearchRequest, Location
from shared.logging import setup_logger, log_function_call, log_function_result, log_function_error

class SearchLocations:
  """Use case for searching locations by city name."""
  def __init__(self, repository: LocationRepository):
    """Initialize the search locations use case.
    
    Args:
      repository: Repository for location data access
    """
    self.repository = repository
    self.logger = setup_logger("search_locations")
  
  async def execute(self, request: LocationSearchRequest) -> List[Location]:
    """Execute the location search.
    
    Args:
      request: Location search request with city name
      
    Returns:
      List of location options matching the city
      
    Raises:
      Exception: If search fails
    """
    log_function_call(self.logger, "execute", {
      "city": request.city
    })
    try:
      locations = await self.repository.search_locations(request)
      log_function_result(self.logger, "execute", {"locations_count": len(locations)})
      return locations
    except Exception as e:
      log_function_error(self.logger, "execute", e, {
        "city": request.city
      })
      raise