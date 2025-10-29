"""Dependency injection container for the application."""
from llms.infrastructure.google_service import GoogleService
from locations.infrastructure.search_locations_tools import SearchLocationTools
from flights.infrastructure.search_flights_tools import SearchFlightsTools
from locations.application.search_locations import SearchLocations
from flights.application.search_flights import SearchFlights
from locations.infrastructure.search_locations_repository import SearchLocationsRepository
from flights.infrastructure.search_flights_repository import SearchFlightsRepository
from amadeus.infrastructure.amadeus_client import AmadeusClient
from shared.logging import setup_logger

logger = setup_logger("dependency_container")

class DependencyContainer:
  """Container for managing application dependencies and their lifecycle."""  
  def __init__(self):
    """Initialize the dependency container."""
    self._amadeus_client = None
    self._llm_service = None
    
    logger.info("Initializing dependency container")
  
  def get_amadeus_client(self) -> AmadeusClient:
    """Get or create an Amadeus client instance.
    
    Returns:
      Singleton AmadeusClient instance
    """
    if self._amadeus_client is None:
        logger.info("Creating AmadeusClient")
        self._amadeus_client = AmadeusClient()
    return self._amadeus_client
  
  def get_llm_service(self) -> GoogleService:
    """Get or create an LLM service instance.
    
    Returns:
      Singleton GoogleService instance
    """
    if self._llm_service is None:
        logger.info("Creating GoogleLLMService")
        self._llm_service = GoogleService()
    return self._llm_service
  
  def get_location_tool(self):
    """Create a location search tool.
    
    Returns:
      Configured location search tool
    """
    logger.info("Creating location search tool provider")
    
    amadeus_client = self.get_amadeus_client()
    
    repository = SearchLocationsRepository(amadeus_client)
    service = SearchLocations(repository)
    
    return SearchLocationTools(service)
  
  def get_flight_tool(self):
    """Create a flight search tool.
    
    Returns:
      Configured flight search tool
    """
    logger.info("Creating flight search tool provider")
    
    amadeus_client = self.get_amadeus_client()
    
    repository = SearchFlightsRepository(amadeus_client)
    service = SearchFlights(repository)
    
    return SearchFlightsTools(service)

_container = None

def get_container() -> DependencyContainer:
  """Get the global dependency container instance.
  
  Returns:
    Singleton DependencyContainer instance
  """
  global _container
  if _container is None:
      _container = DependencyContainer()
  return _container