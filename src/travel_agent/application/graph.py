from langgraph.graph import StateGraph, START, END
from langgraph.prebuilt import tools_condition

from travel_agent.application.state import ConversationState
from travel_agent.application.conditions import has_valid_query, has_query_extracted_info
from shared.logging import setup_logger

logger = setup_logger("workflow_graph")

def create_graph(workflow_nodes) -> StateGraph:  
  graph = StateGraph(ConversationState)

  graph.add_node("location_search_tools_node", workflow_nodes.location_search_tools_node)
  graph.add_node("flight_search_tools_node", workflow_nodes.flight_search_tools_node)
  graph.add_node("check_user_query", workflow_nodes.check_user_query)
  graph.add_node("extractor_node", workflow_nodes.extractor_node)
  graph.add_node("location_search_node", workflow_nodes.location_search_node)
  graph.add_node("process_location_results", workflow_nodes.process_location_results)
  graph.add_node("flight_search_node", workflow_nodes.flight_search_node)
  graph.add_node("process_flight_results", workflow_nodes.process_flight_results)
  graph.add_node("proposal_node", workflow_nodes.proposal_node)

  graph.add_edge(START, "check_user_query")
  graph.add_conditional_edges(
    "check_user_query", has_valid_query,
    {
      True: "extractor_node", 
      False: END
    }
  )
  graph.add_conditional_edges(
    "extractor_node", has_query_extracted_info,
    {
      True: "location_search_node", 
      False: "extractor_node"
    }
  )
  graph.add_conditional_edges(
    "location_search_node", tools_condition,
    {
      "tools": "location_search_tools_node",
      "__end__": "process_location_results"
    }
  )
  graph.add_edge("location_search_tools_node", "location_search_node")
  graph.add_edge("process_location_results", "flight_search_node")
  graph.add_conditional_edges(
    "flight_search_node", tools_condition,
    {
      "tools": "flight_search_tools_node", 
      "__end__": "process_flight_results"
    }
  )
  graph.add_edge("flight_search_tools_node", "flight_search_node")
  graph.add_edge("process_flight_results", "proposal_node")
  graph.add_edge("proposal_node", END)
  
  logger.info("Travel agent workflow graph created successfully")
  return graph