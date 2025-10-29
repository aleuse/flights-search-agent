"""Domain entities for travel agent operations."""
from typing import Optional, Union
from pydantic import BaseModel, Field

class IsValid(BaseModel):
  """Validation result for user queries."""
  is_valid: str = Field(description="The validity of the user's query. It can be 'True' or 'False'.")
  reason: Optional[str]

class QueryExtractedInfo(BaseModel):
  """Extracted travel information from user queries."""
  budget: Optional[Union[float, str]] = Field(description="The maximum price (optional). If not mentioned, set this to null.")
  origin: str = Field(description="The origin city or location (e.g., 'New York', 'Medellin')")
  destination: str = Field(description="The destination city or location (e.g., 'Paris', 'Tokyo')")
  start_date: str = Field(description="The departure date. Format: YYYY-MM-DD")
  end_date: str = Field(description="The return date. Format: YYYY-MM-DD")