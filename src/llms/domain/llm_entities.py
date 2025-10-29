"""Domain entities for LLM operations."""
from dataclasses import dataclass
from typing import List, Any, Optional, Type
from pydantic import BaseModel
from langchain_core.runnables import Runnable
from shared.config import settings

@dataclass
class LLMChainRequest:
  """Request parameters for creating an LLM chain."""
  prompt: str
  tools: Optional[List[Any]] = None
  structured_output: Optional[Type[BaseModel]] = None
  temperature: float = 0.0

@dataclass
class LLMResponse:
  """Response from an LLM operation."""
  content: str
  tool_calls: Optional[List[dict]] = None

@dataclass
class LLM:
  """Configuration for an LLM model."""
  temperature: float = 0.0
  model: str = settings.MODEL_NAME
  api_key: str = settings.GOOGLE_API_KEY

@dataclass
class LLMChain:
  """Wrapper for a LangChain runnable chain."""
  chain: Runnable