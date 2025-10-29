"""Domain entities for flight searches and results."""
from dataclasses import dataclass, field
from typing import Optional, List
from pydantic import BaseModel, Field

@dataclass
class FlightSegment:
  """Represents a single flight segment within an itinerary."""
  departure_code: str
  departure_time: str
  arrival_code: str
  arrival_time: str
  carrier_code: str
  flight_number: str
  aircraft_code: Optional[str] = None
  duration: str = ""
  
  def __str__(self) -> str:
    return f"{self.carrier_code}{self.flight_number}: {self.departure_code} -> {self.arrival_code} ({self.departure_time} - {self.arrival_time})"
  
  def __repr__(self) -> str:
    return self.__str__()

@dataclass
class Itinerary:
  """Represents either an outbound or return itinerary with multiple segments."""
  duration: str
  segments: List[FlightSegment]
  
  def __str__(self) -> str:
    segments_str = " -> ".join([seg.arrival_code for seg in self.segments])
    if self.segments:
      return f"{self.segments[0].departure_code} -> {segments_str} (Duration: {self.duration})"
    return f"Duration: {self.duration}"
  
  def __repr__(self) -> str:
    return self.__str__()

@dataclass
class Flight:
  """Represents a complete flight offer (both outbound and return)."""
  # Basic information
  offer_id: str
  price: float
  currency: str
  
  # Itineraries (outbound is first, return is second)
  outbound: Itinerary
  return_flight: Optional[Itinerary] = None
  
  # Additional details
  last_ticketing_date: Optional[str] = None
  number_of_bookable_seats: Optional[int] = None
  validating_airline_codes: Optional[List[str]] = None
  
  # Computed fields for backward compatibility
  airline: str = field(init=False, default="")
  departure_time: str = field(init=False, default="")
  arrival_time: str = field(init=False, default="")
  duration: str = field(init=False, default="")
  origin_code: str = field(init=False, default="")
  destination_code: str = field(init=False, default="")
  
  def __post_init__(self):
    """Set computed fields based on outbound itinerary."""
    if self.outbound and self.outbound.segments:
      # Compute airline (unique carrier codes from all segments)
      all_segments = self.outbound.segments.copy()
      if self.return_flight and self.return_flight.segments:
        all_segments.extend(self.return_flight.segments)
      
      object.__setattr__(self, 'airline', ", ".join({seg.carrier_code for seg in all_segments}))
      object.__setattr__(self, 'departure_time', self.outbound.segments[0].departure_time)
      
      if self.return_flight and self.return_flight.segments:
        object.__setattr__(self, 'arrival_time', self.return_flight.segments[-1].arrival_time)
      else:
        object.__setattr__(self, 'arrival_time', self.outbound.segments[-1].arrival_time)
      
      if self.return_flight:
        object.__setattr__(self, 'duration', f"{self.outbound.duration} / {self.return_flight.duration}")
      else:
        object.__setattr__(self, 'duration', self.outbound.duration)
      
      object.__setattr__(self, 'origin_code', self.outbound.segments[0].departure_code)
      
      if self.return_flight and self.return_flight.segments:
        object.__setattr__(self, 'destination_code', self.return_flight.segments[-1].arrival_code)
      else:
        object.__setattr__(self, 'destination_code', self.outbound.segments[-1].arrival_code)
  
  def __str__(self) -> str:
    """String representation of the flight"""
    result = f"Flight Offer {self.offer_id}\n"
    result += f"  Price: {self.price} {self.currency}\n"
    result += f"  Outbound: {self.outbound}\n"
    if self.return_flight:
      result += f"  Return: {self.return_flight}\n"
    result += f"  Airlines: {self.airline}\n"
    return result
  
  def __repr__(self) -> str:
    return self.__str__()

class FlightSearchRequest(BaseModel):
  """Request model for flight searches."""
  origin_code: str = Field(description="The origin of the flight. Format: IATA code")
  destination_code: str = Field(description="The destination of the flight. Format: IATA code")
  start_date: str = Field(description="The start date of the flight. Format: YYYY-MM-DD")
  end_date: str = Field(description="The end date of the flight. Format: YYYY-MM-DD")
  max_price: Optional[float] = Field(description="The max price of the flight. Format: USD. If not mentioned, set this to null.")

class FlightSearchResult(BaseModel):
  """Result model for flight searches."""
  flight_results: str = Field(description="The results of the flight search")