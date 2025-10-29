"""LangChain tool for flight searches."""
from typing import List, Optional
import asyncio

from langchain_core.tools import BaseTool
from langchain_core.tools.base import ArgsSchema
from pydantic import Field
from flights.domain.flights_entities import FlightSearchRequest, Flight
from flights.application.search_flights import SearchFlights
from shared.logging import setup_logger, log_function_call, log_function_result, log_function_error

class SearchFlightsTools(BaseTool):
  """LangChain tool wrapper for flight search functionality."""
  name: str = "flight_search"
  description: str = "Search for a flight based on origin, destination, start date, end date, and max price"
  args_schema: ArgsSchema = FlightSearchRequest 
  return_direct: bool = True
  search_flights: Optional[SearchFlights] = Field(default=None, exclude=True)

  def __init__(self, search_flights: SearchFlights):
    """Initialize the flight search tool.
    
    Args:
      search_flights: Search flights use case instance
    """
    super().__init__()
    object.__setattr__(self, 'search_flights', search_flights)
    object.__setattr__(self, 'logger', setup_logger("search_flights_tools"))
    
  def _run(self, origin_code: str, destination_code: str, start_date: str, end_date: str, max_price: int) -> List[Flight]:
    """Synchronous wrapper for the async flight search.
    
    Args:
      origin_code: Origin IATA code
      destination_code: Destination IATA code
      start_date: Departure date
      end_date: Return date
      max_price: Maximum price filter
      
    Returns:
      List of available flights
      
    Raises:
      Exception: If search fails
    """
    log_function_call(self.logger, "SearchFlightsTools._run", {"origin_code": origin_code, "destination_code": destination_code, "start_date": start_date, "end_date": end_date, "max_price": max_price})
    try: 
      flights = asyncio.run(self._arun(origin_code, destination_code, start_date, end_date, max_price))
      return flights
    except Exception as e:
      log_function_error(self.logger, "SearchFlightsTools._run", e, {"origin_code": origin_code, "destination_code": destination_code, "start_date": start_date, "end_date": end_date, "max_price": max_price})
      raise
    
  async def _arun(self, origin_code: str, destination_code: str, start_date: str, end_date: str, max_price: int) -> List[Flight]:
    """Asynchronously search for flights.
    
    Args:
      origin_code: Origin IATA code
      destination_code: Destination IATA code
      start_date: Departure date
      end_date: Return date
      max_price: Maximum price filter
      
    Returns:
      List of available flights
      
    Raises:
      Exception: If search fails
    """
    self.logger.info(f"Searching for flights from {origin_code} to {destination_code}")
    log_function_call(self.logger, "SearchFlightsTools._arun", {"origin_code": origin_code, "destination_code": destination_code, "start_date": start_date, "end_date": end_date, "max_price": max_price})
    
    try:
      request = FlightSearchRequest(origin_code=origin_code, destination_code=destination_code, start_date=start_date, end_date=end_date, max_price=max_price)
      flights = await self.search_flights.execute(request)
      log_function_result(self.logger, "SearchFlightsTools._arun", {"flights_count": len(flights)})
      return flights
    except Exception as e:
      log_function_error(self.logger, "SearchFlightsTools._arun", e, {"origin_code": origin_code, "destination_code": destination_code, "start_date": start_date, "end_date": end_date, "max_price": max_price})
      raise