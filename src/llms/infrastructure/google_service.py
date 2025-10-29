"""Google service implementation for LLM operations."""
from llms.domain.llm_service import LLMService
from llms.domain.llm_entities import LLMChainRequest, LLMResponse, LLMChain
from llms.infrastructure.google_client import GoogleClient
from shared.logging import setup_logger, log_function_call, log_function_result, log_function_error
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from shared.config import settings

class GoogleService(LLMService):
  """Service implementation for Google Generative AI."""
  def __init__(self):
    """Initialize the Google LLM service."""
    self.client = GoogleClient()
    self.logger = setup_logger("google_service")
    
  async def get_chain(self, request: LLMChainRequest) -> LLMResponse:
    """Create an LLM chain based on the request.
    
    Args:
      request: Request containing chain configuration
      
    Returns:
      LLMChain with configured prompt and tools
      
    Raises:
      Exception: If chain creation fails
    """
    log_function_call(self.logger, "generate_response", {
      "prompt": request.prompt,
      "tools": request.tools,
      "structured_output": request.structured_output,
      "temperature": request.temperature
    })
    try:
      llm = self.client.get_llm(temperature=request.temperature, model=settings.MODEL_NAME)
      
      if request.tools:
        llm = llm.bind_tools(request.tools)
        self.logger.info("Tools bound to LLM")
      
      if request.structured_output:
        llm = llm.with_structured_output(request.structured_output)
        self.logger.info("Structured output bound to LLM")
      
      prompt = ChatPromptTemplate.from_messages([
        ("system", request.prompt),
        MessagesPlaceholder(variable_name="messages")
        ],
        template_format="jinja2", 
      )
      chain = prompt | llm 
      return LLMChain(chain=chain)
    except Exception as e:
      log_function_error(self.logger, "generate_response", e, {
        "prompt": request.prompt,
        "tools": request.tools,
        "structured_output": request.structured_output,
        "temperature": request.temperature
      })
      raise 