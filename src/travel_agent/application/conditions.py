from travel_agent.application.state import ConversationState
from shared.logging import setup_logger

logger = setup_logger("edges")

def has_valid_query(state: ConversationState) -> bool:
  logger.debug(f"Checking if query is valid: {state.get('valid_query', False)}")
  return state.get("valid_query", False)

def has_query_extracted_info(state: ConversationState) -> bool:
  has_all_info = all([
    state.get("origin"),
    state.get("destination"),
    state.get("start_date"),
    state.get("end_date")
  ])
  logger.debug(f"Checking if all info extracted: {has_all_info}")
  return has_all_info
