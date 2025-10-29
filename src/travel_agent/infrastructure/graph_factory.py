from travel_agent.application.graph import create_graph
from travel_agent.infrastructure.dependency_injection import get_container
from travel_agent.application.nodes import WorkflowNodes

def get_compiled_graph():
  container = get_container()
  
  nodes = WorkflowNodes(
      llm_service=container.get_llm_service(),
      location_tool=container.get_location_tool(),
      flight_tool=container.get_flight_tool()
  )
  
  graph = create_graph(nodes)
  
  return graph.compile()