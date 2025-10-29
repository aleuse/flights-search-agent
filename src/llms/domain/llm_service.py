"""Abstract interface for LLM services."""
from abc import ABC, abstractmethod
from llms.domain.llm_entities import LLMChainRequest, LLMChain

class LLMService(ABC):
  """Abstract base class for LLM service implementations."""
  @abstractmethod
  async def get_chain(self, request: LLMChainRequest) -> LLMChain:
    pass