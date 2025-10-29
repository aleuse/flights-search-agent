"""Abstract interface for LLM clients."""
from abc import ABC, abstractmethod
from langchain_core.runnables import Runnable
from llms.domain.llm_entities import LLM

class LLMClient(ABC):
  """Abstract base class for language model clients."""
  @abstractmethod
  def get_llm(self, llm: LLM ) -> Runnable:
    pass