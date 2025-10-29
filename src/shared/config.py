"""Configuration settings for the Flight Search Agent application."""
from pathlib import Path
from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
  """Application settings loaded from environment variables.
  
  This class manages all configuration settings for the application,
  including API keys, service endpoints, and rate limiting parameters.
  
  Attributes:
    GOOGLE_API_KEY: API key for Google Generative AI services
    MODEL_NAME: Name of the LLM model to use
    AMADEUS_CLIENT_ID: Client ID for Amadeus API
    AMADEUS_CLIENT_SECRET: Secret key for Amadeus API
    LANGFUSE_PUBLIC_KEY: Public key for Langfuse observability
    LANGFUSE_SECRET_KEY: Secret key for Langfuse observability
    LANGFUSE_HOST: Host URL for Langfuse service
    RATE_LIMIT_MAX_REQUESTS: Maximum number of requests per time window
    RATE_LIMIT_WINDOW_SECONDS: Time window in seconds for rate limiting
  """
  model_config = SettingsConfigDict(env_file=".env")
  GOOGLE_API_KEY: str
  MODEL_NAME: str 
  AMADEUS_CLIENT_ID: str
  AMADEUS_CLIENT_SECRET: str
  LANGFUSE_PUBLIC_KEY: str
  LANGFUSE_SECRET_KEY: str
  LANGFUSE_HOST: str
  
  RATE_LIMIT_MAX_REQUESTS: int = 5
  RATE_LIMIT_WINDOW_SECONDS: int = 60

settings = Settings()