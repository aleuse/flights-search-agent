"""Application use case for creating LLM chains."""
from llms.domain.llm_service import LLMService
from llms.domain.llm_entities import LLMChainRequest, LLMChain
from shared.logging import setup_logger, log_function_call, log_function_result, log_function_error

class GetLLMChain:
  """Use case for creating LLM chains for various purposes."""
  def __init__(self, service: LLMService):
    """Initialize the get LLM chain use case.
    
    Args:
      service: LLM service implementation
    """
    self.service = service
    self.logger = setup_logger("get_llm_chain")
  
  async def execute(self, request: LLMChainRequest) -> LLMChain:
    """Execute the chain creation.
    
    Args:
      request: Request containing chain configuration
      
    Returns:
      Created LLM chain instance
      
    Raises:
      Exception: If chain creation fails
    """
    log_function_call(self.logger, "execute", {
      "prompt": request.prompt,
      "tools": request.tools,
      "structured_output": request.structured_output,
      "temperature": request.temperature
    })
    try:
      chain = await self.service.get_chain(request)
      log_function_result(self.logger, "execute", {
        "chain": chain.chain
      })
      return chain
    except Exception as e:
      log_function_error(self.logger, "execute", e, {
        "prompt": request.prompt,
        "tools": request.tools,
        "structured_output": request.structured_output,
        "temperature": request.temperature
      })
      raise