"""Rate limiting utilities for API requests."""
import time
import asyncio
from typing import Dict
from .config import settings
from .logging import setup_logger

class SimpleRateLimiter:
  """Simple rate limiter with sliding window algorithm.
  
  Limits the number of requests per endpoint within a time window.
  Implements a sliding window approach to enforce rate limits.
  """
  def __init__(self, max_requests: int = None, window_seconds: int = None):
    """Initialize the rate limiter.
    
    Args:
      max_requests: Maximum number of requests per time window
      window_seconds: Length of the time window in seconds
    """
    self.max_requests = max_requests or settings.RATE_LIMIT_MAX_REQUESTS
    self.window_seconds = window_seconds or settings.RATE_LIMIT_WINDOW_SECONDS
    self.requests: Dict[str, list] = {}
    self.lock = asyncio.Lock()
    
    self.logger = setup_logger("rate_limiter")
    self.logger.info(f"Rate limiter initialized: {self.max_requests} requests per {self.window_seconds} seconds")
    
  async def wait_if_needed(self, endpoint: str = "default") -> None:
    """Wait if necessary to enforce rate limits.
    
    Checks the rate limit for the given endpoint and waits if the limit
    has been reached. Cleans up old requests outside the time window.
    
    Args:
      endpoint: Identifier for the endpoint being rate limited
    """
    async with self.lock:
      now = time.time()
      window_start = now - self.window_seconds
      
      if endpoint in self.requests:
        self.requests[endpoint] = [
          req_time for req_time in self.requests[endpoint] 
          if req_time > window_start
        ]
      else:
        self.requests[endpoint] = []
      
      current_requests = len(self.requests[endpoint])
      
      if current_requests >= self.max_requests:
        oldest_request = min(self.requests[endpoint])
        wait_time = (oldest_request + self.window_seconds) - now
        
        if wait_time > 0:
          self.logger.warning(
              f"Rate limit reached for {endpoint} ({current_requests}/{self.max_requests}). "
              f"Waiting {wait_time:.2f} seconds..."
          )
          await asyncio.sleep(wait_time)
          
          now = time.time()
          window_start = now - self.window_seconds
          self.requests[endpoint] = [
            req_time for req_time in self.requests[endpoint] 
            if req_time > window_start
          ]
      
      self.requests[endpoint].append(time.time())
      self.logger.debug(
        f"Request allowed for {endpoint}: "
        f"{len(self.requests[endpoint])}/{self.max_requests}"
      )

rate_limiter = SimpleRateLimiter()