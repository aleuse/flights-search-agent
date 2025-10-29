"""Request handler for web API."""
from web_api.domain.entities import APIRequest, APIResponse
from travel_agent.infrastructure.graph_factory import get_compiled_graph
from travel_agent.application.state import ConversationState
from observability.infrastructure.langfuse_client import langfuse_handler
from shared.logging import setup_logger, log_function_call, log_function_result, log_function_error
from langchain_core.messages import HumanMessage

class HandleRequest:
  """Handles incoming API requests and processes them through the travel agent workflow."""
  def __init__(self):
    """Initialize the request handler with the compiled workflow graph."""
    self.graph = get_compiled_graph()
    self.logger = setup_logger("web_api_handle_request")
    
  async def execute(self, request: APIRequest) -> APIResponse:
    """Execute the request through the travel agent workflow.
    
    Args:
      request: API request containing user query
      
    Returns:
      API response with generated response and state
      
    Raises:
      Exception: If processing fails
    """
    self.logger.info(f"Received request to generate response for query: {request.user_query[:100]}...")
    log_function_call(self.logger, "execute", {
      "user_query_length": len(request.user_query),
      "user_query_preview": request.user_query[:100] + "..." if len(request.user_query) > 100 else request.user_query
    })
    
    try:
      initial_state = ConversationState(
        user_query=request.user_query,
        valid_query=False,
        budget=None,
        origin="",
        origin_code="",
        destination="",
        destination_code="",
        start_date="",
        end_date="",
        flight_results="",
        messages=[HumanMessage(content=request.user_query)]
        )
      
      self.logger.debug("Calling travel agent workflow")
      output  = await self.graph.ainvoke(
        input=initial_state,
        config={
          "callbacks": [langfuse_handler]
        }
      )
      response = output["messages"][-1]
      result = APIResponse(response=response, state=output)
      
      log_function_result(self.logger, "execute", {
        "response_length": len(response),
        "response_preview": response[:100] + "..." if len(response) > 100 else response,
        "final_state_keys": list(output.keys()) if isinstance(output, dict) else "not_dict"
      })
      
      self.logger.info("Request handled successfully")
      return result
        
    except Exception as e:
      log_function_error(self.logger, "execute", e, {
        "user_query_length": len(request.user_query),
        "user_query_preview": request.user_query[:100] + "..." if len(request.user_query) > 100 else request.user_query
      })
      self.logger.error(f"Failed to handle request for query: {request.user_query[:100]}...")
      return APIResponse(response=f"Error processing request: {str(e)}", state={})
