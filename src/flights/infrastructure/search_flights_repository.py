"""Repository implementation for flight searches using Amadeus API."""
from typing import List
from amadeus.infrastructure.amadeus_client import AmadeusClient
from flights.domain.flights_repository import FlightRepository
from flights.domain.flights_entities import FlightSearchRequest, Flight, Itinerary, FlightSegment
from shared.logging import setup_logger, log_function_call, log_function_result, log_function_error

class SearchFlightsRepository(FlightRepository):
  """Repository implementation for searching flights via Amadeus API."""
  def __init__(self, client: AmadeusClient):
    """Initialize the flight search repository.
    
    Args:
      client: Amadeus API client instance
    """
    self.client = client
    self.logger = setup_logger("search_flights_repository")
    
  async def search_flights(self, request: FlightSearchRequest) -> List[Flight]:
    """Search for flights using the Amadeus API.
    
    Args:
      request: Flight search request with criteria
      
    Returns:
      List of flight offers matching the search criteria
      
    Raises:
      Exception: If search fails
    """
    log_function_call(self.logger, "search_flights", {
      "origin": request.origin_code,
      "destination": request.destination_code,
      "start_date": request.start_date,
      "end_date": request.end_date
    })
    
    try:
      raw_data = self.client.search_flights(
        origin=request.origin_code,
        destination=request.destination_code,
        start_date=request.start_date,
        end_date=request.end_date,
        max_price=request.max_price
      )
      flights = self._parse_flights(raw_data)
      log_function_result(self.logger, "search_flights", {"flights_count": len(flights)})
      return flights
    except Exception as e:
      log_function_error(self.logger, "search_flights", e, {
        "origin": request.origin_code,
        "destination": request.destination_code,
        "start_date": request.start_date,
        "end_date": request.end_date
      })
      raise
      
  def _parse_flights(self, raw_data: dict) -> List[Flight]:
    """Parse raw flight data from Amadeus API into domain entities.
    
    Args:
      raw_data: Raw flight data from API response
      
    Returns:
      List of Flight domain entities
    """
    flights = []
    if isinstance(raw_data, dict) and "data" in raw_data:
      for offer in raw_data["data"]:
        # Parse itineraries
        itineraries_data = offer.get("itineraries", [])
        
        # Parse outbound itinerary (first one)
        outbound = self._parse_itinerary(itineraries_data[0]) if itineraries_data else None
        
        # Parse return itinerary (second one, if exists)
        return_flight = self._parse_itinerary(itineraries_data[1]) if len(itineraries_data) > 1 else None
        
        # Parse price and additional info
        price_data = offer.get("price", {})
        validating_airlines = offer.get("validatingAirlineCodes", [])
        
        flight = Flight(
          offer_id=offer.get("id", ""),
          price=float(price_data.get("total", "0")),
          currency=price_data.get("currency", "USD"),
          outbound=outbound,
          return_flight=return_flight,
          last_ticketing_date=offer.get("lastTicketingDate"),
          number_of_bookable_seats=offer.get("numberOfBookableSeats"),
          validating_airline_codes=validating_airlines
        )
        flights.append(flight)
    return flights
  
  def _parse_itinerary(self, itinerary_data: dict) -> Itinerary:
    """Parse a single itinerary (outbound or return).
    
    Args:
      itinerary_data: Raw itinerary data from API
      
    Returns:
      Itinerary domain entity with parsed segments
    """
    segments_data = itinerary_data.get("segments", [])
    segments = []
    
    for seg in segments_data:
      departure = seg.get("departure", {})
      arrival = seg.get("arrival", {})
      
      segment = FlightSegment(
        departure_code=departure.get("iataCode", ""),
        departure_time=departure.get("at", ""),
        arrival_code=arrival.get("iataCode", ""),
        arrival_time=arrival.get("at", ""),
        carrier_code=seg.get("carrierCode", ""),
        flight_number=seg.get("number", ""),
        aircraft_code=seg.get("aircraft", {}).get("code"),
        duration=seg.get("duration", "")
      )
      segments.append(segment)
    
    return Itinerary(
      duration=itinerary_data.get("duration", ""),
      segments=segments
    )