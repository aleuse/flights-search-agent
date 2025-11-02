from travel_agent.application.nodes import WorkflowNodes
from travel_agent.infrastructure.dependency_injection import DependencyContainer
from shared.logging import setup_logger

logger = setup_logger("workflow_factory")

def create_travel_agent_workflow(container: DependencyContainer) -> WorkflowNodes:
  logger.info("Creating travel agent workflow with dependencies")
  
  nodes = WorkflowNodes(
      llm_service=container.get_llm_service(),  
      location_tool=container.get_location_tool(),
      flight_tool=container.get_flight_tool()
  )
  
  logger.info("Travel agent workflow created successfully")
  return nodes
