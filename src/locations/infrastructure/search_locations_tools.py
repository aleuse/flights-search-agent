"""LangChain tool for location searches."""
from typing import List, Optional
import asyncio

from langchain_core.tools import BaseTool
from langchain_core.tools.base import ArgsSchema
from pydantic import Field
from locations.domain.location_entities import LocationSearchRequest, Location
from locations.application.search_locations import SearchLocations
from shared.logging import setup_logger, log_function_call, log_function_result, log_function_error

class SearchLocationTools(BaseTool):
  """LangChain tool wrapper for location search functionality."""
  name: str = "location_search"
  description: str = "Search for a location code based on a keyword. The keyword is the city name."
  args_schema: ArgsSchema = LocationSearchRequest  
  return_direct: bool = True
  search_locations: Optional[SearchLocations] = Field(default=None, exclude=True)
  
  def __init__(self, search_locations: SearchLocations):
    """Initialize the location search tool.
    
    Args:
      search_locations: Search locations use case instance
    """
    super().__init__()
    object.__setattr__(self, 'search_locations', search_locations)
    object.__setattr__(self, 'logger', setup_logger("search_location_tools"))
    
  def _run(self, city: str) -> List[Location]:
    """Synchronous wrapper for the async location search.
    
    Args:
      city: City name to search for
      
    Returns:
      List of location results
      
    Raises:
      Exception: If search fails
    """
    log_function_call(self.logger, "SearchLocationTools._run", {"city": city})
    try: 
      locations = asyncio.run(self._arun(city))
      return locations
    except Exception as e:
      log_function_error(self.logger, "SearchLocationTools._run", e, {"city": city})
      raise
    
  async def _arun(self, city: str) -> List[Location]:
    """Asynchronously search for locations.
    
    Args:
      city: City name to search for
      
    Returns:
      List of location results
      
    Raises:
      Exception: If search fails
    """
    self.logger.info(f"Searching for location: {city}")
    log_function_call(self.logger, "SearchLocationTools._arun", {"city": city})
    
    try:
      request = LocationSearchRequest(city=city)
      locations = await self.search_locations.execute(request)
      log_function_result(self.logger, "SearchLocationTools._arun", {"locations_count": len(locations)})
      return locations
    except Exception as e:
      log_function_error(self.logger, "SearchLocationTools._arun", e, {"city": city})
      raise
