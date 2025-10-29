"""Travel-related domain entities."""
from dataclasses import dataclass
from typing import Optional, List
from flights.domain.flights_entities import Flight

@dataclass
class TravelRequest:
  """Request for travel information."""
  origin: str
  destination: str
  start_date: str
  end_date: str
  budget: Optional[float] = None

@dataclass
class TravelProposal:
  """Proposal for travel options."""
  request: TravelRequest
  flights: List[Flight]
  total_cost: float
  proposal: str