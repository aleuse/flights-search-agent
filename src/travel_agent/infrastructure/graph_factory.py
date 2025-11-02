from travel_agent.application.graph import create_graph
from travel_agent.infrastructure.dependency_injection import get_container
from travel_agent.infrastructure.workflow_factory import create_travel_agent_workflow

def get_compiled_graph():
  container = get_container()
  
  nodes = create_travel_agent_workflow(container)
  
  graph = create_graph(nodes)
  compiled_graph = graph.compile()
  
  from IPython.display import Image, display  
  display(Image(compiled_graph.get_graph(xray=True).draw_mermaid_png()))
  
  return compiled_graph