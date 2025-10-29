"""Domain entities for location searches."""
from dataclasses import dataclass
from pydantic import BaseModel, Field

@dataclass
class Location:
  """Represents a location with IATA code."""
  name: str
  iata_code: str
  country: str

class LocationSearchRequest(BaseModel):
  """Request model for location searches."""
  city: str = Field(description="The city to search for")

class LocationSearchResult(BaseModel):
  """Result model for location searches."""
  origin_code: str = Field(description="The IATA code of the origin city")
  destination_code: str = Field(description="The IATA code of the destination city")
