from langfuse import Langfuse
from langfuse.langchain import CallbackHandler
from shared.config import settings
from shared.logging import setup_logger

logger = setup_logger("langfuse_client")
langfuse_client = Langfuse(
  public_key=settings.LANGFUSE_PUBLIC_KEY,
  secret_key=settings.LANGFUSE_SECRET_KEY,
  host=settings.LANGFUSE_HOST
)

langfuse_handler = CallbackHandler(
  public_key=settings.LANGFUSE_PUBLIC_KEY
)
if langfuse_client.auth_check():
    logger.info("Langfuse client is authenticated and ready!")
else:
    logger.error("Authentication failed. Please check your credentials and host.")