"""Application use case for searching flights."""
from typing import List
from flights.domain.flights_repository import FlightRepository
from flights.domain.flights_entities import FlightSearchRequest, Flight
from shared.logging import setup_logger, log_function_call, log_function_result, log_function_error

class SearchFlights:
  """Use case for searching flights based on travel criteria."""
  def __init__(self, repository: FlightRepository):
    """Initialize the search flights use case.
    
    Args:
      repository: Repository for flight data access
    """
    self.repository = repository
    self.logger = setup_logger("flight_search_use_case")
  
  async def execute(self, request: FlightSearchRequest) -> List[Flight]:
    """Execute the flight search.
    
    Args:
      request: Flight search request with criteria
      
    Returns:
      List of flight options matching the criteria
      
    Raises:
      Exception: If search fails
    """
    log_function_call(self.logger, "execute", {
      "origin": request.origin_code,
      "destination": request.destination_code,
      "start_date": request.start_date,
      "end_date": request.end_date
    })
    
    try:
      flights = await self.repository.search_flights(request)
      log_function_result(self.logger, "execute", {"flights_count": len(flights)})
      return flights
    except Exception as e:
      log_function_error(self.logger, "execute", e, {
        "origin": request.origin_code,
        "destination": request.destination_code
      })
      raise