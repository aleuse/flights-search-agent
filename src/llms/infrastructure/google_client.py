"""Google Generative AI client implementation."""
from langchain_google_genai import ChatGoogleGenerativeAI
from llms.domain.llm_client import LLMClient
from shared.config import settings
from shared.logging import setup_logger, log_function_call, log_function_result, log_function_error

class GoogleClient(LLMClient):
  """Client for interacting with Google's Generative AI."""
  def __init__(self):
    """Initialize the Google Generative AI client."""
    self.logger = setup_logger("google_client")
    self.logger.info("Initializing GoogleClient")
    
  def get_llm(self, temperature: float = 0.0, model: str = settings.MODEL_NAME) -> ChatGoogleGenerativeAI:
    """Get a configured LLM instance.
    
    Args:
      temperature: Sampling temperature for the model
      model: Name of the model to use
      
    Returns:
      Configured ChatGoogleGenerativeAI instance
      
    Raises:
      Exception: If LLM creation fails
    """
    log_function_call(self.logger, "get_llm", {
      "temperature": temperature,
      "model": model
    })
    try:
      llm = ChatGoogleGenerativeAI(
        model=model,
        temperature=temperature,
        api_key=settings.GOOGLE_API_KEY
      )
      log_function_result(self.logger, "get_llm", {"llm": llm})
      return llm
    except Exception as e:
      log_function_error(self.logger, "get_llm", e, {
        "temperature": temperature,
        "model": model
      })
      raise