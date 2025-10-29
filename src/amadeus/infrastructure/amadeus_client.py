"""Amadeus API client for flight and location searches."""
import requests
from typing import List, Dict
from shared.config import settings
from shared.logging import setup_logger, log_function_call, log_function_result, log_function_error

class AmadeusClient:
  """Client for interacting with the Amadeus API.
  
  Handles authentication, location searches, and flight searches
  using the Amadeus Test API endpoints.
  """
  def __init__(self):
    """Initialize the Amadeus client and obtain access token."""
    self.logger = setup_logger("amadeus_client")
    self.logger.info("Initializing AmadeusClient")
    self.client_id = settings.AMADEUS_CLIENT_ID
    self.client_secret = settings.AMADEUS_CLIENT_SECRET
    self.logger.debug("Getting access token")
    self.access_token = self.get_access_token()
    self.logger.info("AmadeusClient initialized successfully")
  
  def get_access_token(self) -> str:
    """Obtain an OAuth2 access token from Amadeus API.
    
    Returns:
      Access token string for API authentication
      
    Raises:
      Exception: If token request fails
    """
    self.logger.info("Getting access token from Amadeus API")
    log_function_call(self.logger, "get_access_token", {"client_id": self.client_id[:8] + "..."})
    
    url = "https://test.api.amadeus.com/v1/security/oauth2/token"
    headers = {"Content-Type": "application/x-www-form-urlencoded"}
    data = {
        "grant_type": "client_credentials",
        "client_id": self.client_id,
        "client_secret": self.client_secret
    }
    
    try:
      self.logger.debug("Making POST request to Amadeus token endpoint")
      response = requests.post(url, headers=headers, data=data)
      response.raise_for_status()
      
      token_data = response.json()
      access_token = token_data["access_token"]
      
      log_function_result(self.logger, "get_access_token", {"token_length": len(access_token)})
      self.logger.info("Access token obtained successfully")
      return access_token
        
    except Exception as e:
      log_function_error(self.logger, "get_access_token", e)
      self.logger.error("Failed to get access token")
      raise
  
  def search_flights(self, origin: str, destination: str, start_date: str, end_date: str, max_price: int = 99999, adults: int = 1) -> list[dict]:
    """Search for flight offers between origin and destination.
    
    Args:
      origin: IATA code of the origin airport
      destination: IATA code of the destination airport
      start_date: Departure date (YYYY-MM-DD)
      end_date: Return date (YYYY-MM-DD)
      max_price: Maximum price filter in USD
      adults: Number of adult passengers
      
    Returns:
      List of flight offers matching the search criteria
      
    Raises:
      Exception: If flight search fails
    """
    self.logger.info(f"Searching flights from {origin} to {destination}")
    log_function_call(self.logger, "search_flights", {
      "origin": origin,
      "destination": destination,
      "start_date": start_date,
      "end_date": end_date,
      "max_price": max_price,
      "adults": adults
    })
    
    url = f"https://test.api.amadeus.com/v2/shopping/flight-offers"
    headers = {"Authorization": f"Bearer {self.access_token}"}
    params = {
      "originLocationCode": origin,
      "destinationLocationCode": destination,
      "departureDate": start_date,
      "returnDate": end_date,
      "maxPrice": max_price,
      "adults": adults,
      "max": 1
    }
    
    try:
      self.logger.debug(f"Making GET request to flight offers endpoint with params: {params}")
      response = requests.get(url, headers=headers, params=params)
      response.raise_for_status()
      
      result = response.json()
      log_function_result(self.logger, "search_flights", {
          "origin": origin,
          "destination": destination,
          "result_count": len(result.get("data", [])) if isinstance(result, dict) else len(result) if isinstance(result, list) else "unknown"
      })
      self.logger.info(f"Flight search completed from {origin} to {destination}")
      return result
        
    except Exception as e:
      log_function_error(self.logger, "search_flights", e, {
        "origin": origin,
        "destination": destination,
        "start_date": start_date,
        "end_date": end_date,
        "max_price": max_price,
        "adults": adults
      })
      self.logger.error(f"Failed to search flights from {origin} to {destination}")
      raise
    
  def search_locations(self, keyword: str) -> list[dict]:
    """Search for location codes by city name.
    
    Args:
      keyword: City name or keyword to search for
      
    Returns:
      List of location objects with IATA codes
      
    Raises:
      Exception: If location search fails
    """
    self.logger.info(f"Searching locations for keyword: {keyword}")
    log_function_call(self.logger, "search_locations", {"keyword": keyword})
    
    url = f"https://test.api.amadeus.com/v1/reference-data/locations"
    headers = {
      "Authorization": f"Bearer {self.access_token}"
    }
    params = {
      "subType": "CITY",
      "keyword": keyword
    }
    
    try:
      self.logger.debug(f"Making GET request to locations endpoint with params: {params}")
      response =  requests.get(url, headers=headers, params=params)
      response.raise_for_status()
      
      result = response.json()
      log_function_result(self.logger, "search_locations", {
        "keyword": keyword,
        "result_count": len(result.get("data", [])) if isinstance(result, dict) else len(result) if isinstance(result, list) else "unknown"
      })
      self.logger.info(f"Location search completed for keyword: {keyword}")
      return result
      
    except Exception as e:
      log_function_error(self.logger, "search_locations", e, {"keyword": keyword})
      self.logger.error(f"Failed to search locations for keyword: {keyword}")
      raise