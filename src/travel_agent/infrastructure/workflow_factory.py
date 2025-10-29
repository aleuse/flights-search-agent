from travel_agent.application.nodes import WorkflowNodes
from travel_agent.application.graph import create_graph
from travel_agent.infrastructure.dependency_injection import DependencyContainer
from shared.logging import setup_logger

logger = setup_logger("workflow_factory")

def create_travel_agent_workflow() -> WorkflowNodes:
  logger.info("Creating travel agent workflow with dependencies")
  
  container = DependencyContainer()
  
  nodes = WorkflowNodes(
      llm_service=container.get_llm_service(),  
      location_tool_provider=container.get_location_tool_provider(),
      flight_tool_provider=container.get_flight_tool_provider()
  )
  
  logger.info("Travel agent workflow created successfully")
  return nodes

def get_workflow_functions() -> dict:
  nodes = create_travel_agent_workflow()
  
  return {
    "check_user_query": nodes.check_user_query,
  }