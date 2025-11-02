from typing import Any
from langchain_core.messages import AIMessage
from langgraph.prebuilt import ToolNode
from langchain_core.tools import BaseTool
from travel_agent.application.state import ConversationState
from llms.domain.llm_service import LLMService
from shared.logging import setup_logger, log_function_call, log_function_result, log_function_error
from shared.rate_limiter import rate_limiter
from shared.config import Settings

class WorkflowNodes:
  def __init__(self, llm_service: LLMService, location_tool: BaseTool, flight_tool: BaseTool):
    self.llm_service = llm_service
    self.location_tool = location_tool
    self.flight_tool = flight_tool
    
    self.location_search_tools_node = ToolNode([self.location_tool])
    self.flight_search_tools_node = ToolNode([self.flight_tool])

    self.logger = setup_logger("workflow_nodes")
  
  async def check_user_query(self, state: ConversationState) -> dict[str, Any]:
    self.logger.info("Starting check_user_query node")
    log_function_call(self.logger, "check_user_query", {"user_query": state.get("user_query", "")})

    from travel_agent.domain.prompts import CHECK_USER_QUERY_PROMPT
    from llms.domain.llm_entities import LLMChainRequest
    from travel_agent.domain.entities import IsValid
    
    user_query = state.get("user_query", "")
    
    chain_request = LLMChainRequest(
      prompt=CHECK_USER_QUERY_PROMPT.prompt,
      structured_output=IsValid,
      temperature=0.0,
    )
    
    await rate_limiter.wait_if_needed("check_user_query")
    response_chain = await self.llm_service.get_chain(chain_request)
    try:
      self.logger.info("Invoking response chain")
      log_function_call(self.logger, "invoke_response_chain", {"user_query": user_query})
      response = await response_chain.chain.ainvoke(
        {
          "messages": state["messages"],
          "user_query": user_query
        }
      )
      log_function_result(self.logger, "invoke_response_chain", {"response": response})
      return {
        "messages": [AIMessage(content=response.reason or "")],
        "valid_query": response.is_valid == 'True',
        "reason": getattr(response, 'reason', None),
        "user_query": user_query
      }
    except Exception as e:
      log_function_error(self.logger, "invoke_response_chain", e, {"user_query": user_query})
      raise

  async def extractor_node(self,state: ConversationState) -> dict[str, Any]:
    self.logger.info("Starting extractor_node")
    log_function_call(self.logger, "extractor_node", {"messages_count": len(state.get("messages", []))})
    
    from travel_agent.domain.prompts import EXTRACT_QUERY_INFO_PROMPT
    from llms.domain.llm_entities import LLMChainRequest
    from travel_agent.domain.entities import QueryExtractedInfo
    
    chain_request = LLMChainRequest(
      prompt=EXTRACT_QUERY_INFO_PROMPT.prompt,
      structured_output=QueryExtractedInfo,
      temperature=0.0,
    )
    
    await rate_limiter.wait_if_needed("extractor_node")  
    response_chain = await self.llm_service.get_chain(chain_request)
    try:
      self.logger.info("Invoking response chain for query information extraction")
      response = await response_chain.chain.ainvoke(
        {
          "messages": state["messages"],
          "user_query": state["user_query"]
        }
      )
      log_function_result(self.logger, "extractor_node", {"response": str(response)})
      result = {
        "budget": response.budget,
        "origin": response.origin,
        "destination": response.destination,
        "start_date": response.start_date,
        "end_date": response.end_date,
        "messages": [AIMessage(content=f"Extracted: {response.origin} -> {response.destination} ({response.start_date} to {response.end_date})")]
      }
      
      log_function_result(self.logger, "extractor_node", {
        "budget": response.budget,
        "origin": response.origin,
        "destination": response.destination,
        "start_date": response.start_date,
        "end_date": response.end_date
      })
      self.logger.info(f"Query extraction completed. Origin: {response.origin}, Destination: {response.destination}")
      return result
    except Exception as e:
      log_function_error(self.logger, "extractor_node", e, {"messages_count": len(state.get("messages", []))})
      return {"messages": [AIMessage(content=f"Error: {e}")]}
      
  async def location_search_node(self, state: ConversationState) -> dict[str, Any]:
    self.logger.info("Starting location_search_node")
    log_function_call(self.logger, "location_search_node", {
      "origin": state.get("origin"),
      "destination": state.get("destination"),
      "messages_count": len(state.get("messages", []))
    })
    
    from travel_agent.domain.prompts import LOCATION_SEARCH_PROMPT
    from llms.domain.llm_entities import LLMChainRequest
    
    chain_request = LLMChainRequest(
      prompt=LOCATION_SEARCH_PROMPT.prompt,
      tools=[self.location_tool],
      temperature=0.0,
    )
    
    await rate_limiter.wait_if_needed("location_search_node")
    
    response_chain = await self.llm_service.get_chain(chain_request)
    try:
      self.logger.info("Invoking response chain for location search")
      response = await response_chain.chain.ainvoke(
        {
          "messages": state["messages"],
          "origin": state.get("origin"),
          "destination": state.get("destination")
        }
      )
      log_function_result(self.logger, "location_search_node", {"response": str(response)})
      
      result = {
        "messages": [response]
      }
      
      log_function_result(self.logger, "location_search_node", {
        "has_tool_calls": bool(getattr(response, 'tool_calls', None)),
        "response_type": type(response).__name__
      })
      self.logger.info(f"Location search node completed. Has tool calls: {bool(getattr(response, 'tool_calls', None))}")
      return result
    except Exception as e:
      log_function_error(self.logger, "location_search_node", e, {
        "origin": state.get("origin"),
        "destination": state.get("destination")
      })
      return {"messages": [AIMessage(content=f"Error: {e}")]}
    
  async def process_location_results(self, state: ConversationState) -> dict[str, Any]:
    self.logger.info("Starting process_location_results")
    log_function_call(self.logger, "process_location_results", {
      "messages_count": len(state.get("messages", []))
    })
    
    from travel_agent.domain.prompts import PROCESS_LOCATION_RESULTS_PROMPT
    from llms.domain.llm_entities import LLMChainRequest
    from locations.domain.location_entities import LocationSearchResult
    
    chain_request = LLMChainRequest(
      prompt=PROCESS_LOCATION_RESULTS_PROMPT.prompt,
      structured_output=LocationSearchResult,
      temperature=0.0,
    )
    
    await rate_limiter.wait_if_needed("process_location_results")
    
    response_chain = await self.llm_service.get_chain(chain_request)
    try:
      self.logger.info("Invoking response chain for location results processing")
      response = await response_chain.chain.ainvoke(
        {
          "messages": state["messages"],
          "origin_code": state.get("origin_code"),
          "destination_code": state.get("destination_code")
        }
      )
      log_function_result(self.logger, "process_location_results", {"response": str(response)})
      result = {
        "origin_code": str(response.origin_code),
        "destination_code": str(response.destination_code),
        "messages": [AIMessage(content=str(response))]
      }
      log_function_result(self.logger, "process_location_results", {
        "origin_code": response.origin_code,
        "destination_code": response.destination_code
      })
      self.logger.info(f"Location results processed. Origin: {response.origin_code}, Destination: {response.destination_code}")
      return result
    except Exception as e:
      log_function_error(self.logger, "process_location_results", e, {
        "messages_count": len(state.get("messages", []))
      })
      return {"messages": [AIMessage(content=f"Error processing location results: {e}")]}

  async def flight_search_node(self, state: ConversationState) -> dict[str, Any]:
    self.logger.info("Starting flight_search_node")
    log_function_call(self.logger, "flight_search_node", {
      "origin": state.get("origin"),
      "destination": state.get("destination"),
      "start_date": state.get("start_date"),
      "end_date": state.get("end_date"),
      "budget": state.get("budget"),
      "messages_count": len(state.get("messages", []))
    })
    
    from travel_agent.domain.prompts import FLIGHT_SEARCH_PROMPT
    from llms.domain.llm_entities import LLMChainRequest
    
    chain_request = LLMChainRequest(
      prompt=FLIGHT_SEARCH_PROMPT.prompt,
      tools=[self.flight_tool],
      temperature=0.0,
    )
    await rate_limiter.wait_if_needed("flight_search_node")
    
    response_chain = await self.llm_service.get_chain(chain_request)
    try:
      self.logger.info("Invoking response chain for flight search")
      response = await response_chain.chain.ainvoke(
        {
          "messages": state["messages"],
          "origin_code": str(state.get("origin_code")),
          "destination_code": str(state.get("destination_code")),
          "start_date": str(state.get("start_date")),
          "end_date": str(state.get("end_date")),
          "budget": str(state.get("budget"))
        }
      )
      log_function_result(self.logger, "flight_search_node", {"response": str(response)})
      result = {
        "messages": [response]
      }
      log_function_result(self.logger, "flight_search_node", {
        "has_tool_calls": bool(getattr(response, 'tool_calls', None)),
        "response_type": type(response).__name__
      })
      log_function_result(self.logger, "flight_search_node", {"response_type": type(response).__name__})
      self.logger.info(f"Flight search node completed. Has tool calls: {bool(getattr(response, 'tool_calls', None))}")
      return result
    except Exception as e:
      log_function_error(self.logger, "flight_search_node", e, {
        "origin": state.get("origin"),
        "destination": state.get("destination"),
        "start_date": state.get("start_date"),
        "end_date": state.get("end_date"),
        "budget": state.get("budget"),
        "messages_count": len(state.get("messages", []))
      })
      return {"messages": [AIMessage(content=f"Error: {e}")]}

  async def process_flight_results(self, state: ConversationState) -> dict[str, Any]:
    self.logger.info("Starting process_flight_results")
    log_function_call(self.logger, "process_flight_results", {
      "messages_count": len(state.get("messages", []))
    })
    
    from travel_agent.domain.prompts import PROCESS_FLIGHT_RESULTS_PROMPT
    from llms.domain.llm_entities import LLMChainRequest
    from flights.domain.flights_entities import FlightSearchResult
    
    chain_request = LLMChainRequest(
      prompt=PROCESS_FLIGHT_RESULTS_PROMPT.prompt,
      structured_output=FlightSearchResult,
      temperature=0.0,
    )
    await rate_limiter.wait_if_needed("process_flight_results")
    
    response_chain = await self.llm_service.get_chain(chain_request)
    try:
      self.logger.info("Invoking response chain for flight results processing")
      response = await response_chain.chain.ainvoke(
        {
          "messages": state["messages"],
          "flight_results": state.get("flight_results")
        }
      )
      log_function_result(self.logger, "process_flight_results", {"response": str(response)})
      result = {
        "flight_results": str(response.flight_results),
        "messages": [AIMessage(content=str(response))]
      }
      log_function_result(self.logger, "process_flight_results", {
        "flight_results": str(response.flight_results)
      })
      self.logger.info(f"Flight results processed. Flight results: {str(response.flight_results)}")
      return result
    except Exception as e:
      log_function_error(self.logger, "process_flight_results", e, {
        "messages_count": len(state.get("messages", []))
      })
      return {"messages": [AIMessage(content=f"Error processing flight results: {e}")]}

  async def proposal_node(self, state: ConversationState) -> dict[str, Any]:
    self.logger.info("Starting proposal_node")
    log_function_call(self.logger, "proposal_node", {
      "budget": state.get("budget"),
      "origin": state.get("origin"),
      "destination": state.get("destination"),
      "start_date": state.get("start_date"),
      "end_date": state.get("end_date"),
      "messages_count": len(state.get("messages", []))
    })
    
    from travel_agent.domain.prompts import PROPOSE_TRAVEL_PLAN_PROMPT
    from llms.domain.llm_entities import LLMChainRequest
    
    chain_request = LLMChainRequest(
      prompt=PROPOSE_TRAVEL_PLAN_PROMPT.prompt,
      temperature=0.0,
    ) 
    await rate_limiter.wait_if_needed("proposal_node")
    
    response_chain = await self.llm_service.get_chain(chain_request)
    try:
      self.logger.info("Invoking response chain for travel proposal generation")
      response = await response_chain.chain.ainvoke(
        {
          "messages": state["messages"],
          "budget": str(state["budget"]),
          "origin": str(state["origin"]),
          "destination": str(state["destination"]),
          "start_date": str(state["start_date"]),
          "end_date": str(state["end_date"]),
          "flight_results": str(state["flight_results"])
        }
      )
      log_function_result(self.logger, "proposal_node", {"response": str(response)})
      result = {"messages": [response.content[-1]]}
      log_function_result(self.logger, "proposal_node", {"response_type": type(response).__name__})
      self.logger.info("Travel proposal generation completed successfully")
      return result
    except Exception as e:
      log_function_error(self.logger, "proposal_node", e, {
        "budget": state.get("budget"),
        "origin": state.get("origin"),
        "destination": state.get("destination"),
        "start_date": state.get("start_date"),
        "end_date": state.get("end_date")
      })
      return {"messages": [AIMessage(content=f"Error: {e}")]}