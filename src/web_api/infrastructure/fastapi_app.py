"""FastAPI application for the Travel Agent API."""
from fastapi import FastAPI
import uvicorn
from shared.logging import setup_logger

app = FastAPI(title="Travel Agent API")

logger = setup_logger("web_api")
from web_api.infrastructure.handle_request import HandleRequest
from web_api.domain.entities import APIRequest

@app.post("/generate-response")
async def generate_response_endpoint(user_query: str):
  """Generate a response to a user query using the travel agent.
  
  Args:
    user_query: The user's travel query
    
  Returns:
    Dictionary containing the response and state
  """
  use_case = HandleRequest()
  request = APIRequest(user_query=user_query)
  result = await use_case.execute(request)
  return {"response": result.response, "state": result.state}

if __name__ == "__main__":
  logger.info("Starting FastAPI application")
  uvicorn.run(app, host="0.0.0.0", port=8000)