"""Domain entities for web API requests and responses."""
from dataclasses import dataclass
from typing import Dict, Any

@dataclass
class APIRequest:
  """Request entity for API operations."""
  user_query: str

@dataclass
class APIResponse:
  """Response entity for API operations."""
  response: str
  state: Dict[str, Any]