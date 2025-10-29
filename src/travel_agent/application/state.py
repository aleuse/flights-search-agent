from typing import Annotated, Optional, Any
from typing_extensions import TypedDict
from operator import add
from langchain_core.messages import BaseMessage

class ConversationState(TypedDict):
  user_query: str
  valid_query: bool
  budget: Optional[float]
  origin: str
  origin_code: str
  destination: str
  destination_code: str
  start_date: str
  end_date: str
  flight_results: str
  messages: Annotated[list[BaseMessage], add]