"""Logging utilities for the Flight Search Agent application."""
import logging
import sys
from pathlib import Path
from datetime import datetime
from typing import Any, Dict, Optional
import json

def setup_logger(name: str, level: str = "INFO") -> logging.Logger:
  """Set up a logger with file and console handlers.
  
  Creates a logger that writes to both a file and the console.
  Log files are organized by date in the logs directory.
  
  Args:
    name: Name of the logger
    level: Logging level (default: INFO)
    
  Returns:
    Configured logger instance
  """
  logger = logging.getLogger(name)
  logger.setLevel(getattr(logging, level.upper()))
  
  if logger.handlers:
    return logger

  logs_dir = "logs"
  logs_dir.mkdir(exist_ok=True)
  
  log_file = logs_dir / f"{name}_{datetime.now().strftime('%Y-%m-%d')}.log"
  file_handler = logging.FileHandler(log_file, encoding="utf-8")
  file_handler.setLevel(logging.DEBUG)
  
  console_handler = logging.StreamHandler(sys.stdout)
  console_handler.setLevel(logging.INFO)
  
  formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(funcName)s:%(lineno)d - %(message)s'
    )
  file_handler.setFormatter(formatter)
  console_handler.setFormatter(formatter)
  
  logger.addHandler(file_handler)
  logger.addHandler(console_handler)
  
  return logger

def log_function_call(logger: logging.Logger, func_name: str, params: Dict[str, Any], 
                    level: str = "INFO") -> None:
  """Log a function call with its parameters.
  
  Args:
    logger: Logger instance to use
    func_name: Name of the function being called
    params: Dictionary of parameters passed to the function
    level: Logging level (default: INFO)
  """
  log_level = getattr(logging, level.upper())
  logger.log(log_level, f"Calling {func_name} with params: {json.dumps(params, default=str, indent=2)}")

def log_function_result(logger: logging.Logger, func_name: str, result: Any, 
                    level: str = "INFO") -> None:
  """Log a function result.
  
  Args:
    logger: Logger instance to use
    func_name: Name of the function that completed
    result: Result returned by the function
    level: Logging level (default: INFO)
  """
  log_level = getattr(logging, level.upper())
  logger.log(log_level, f"{func_name} completed successfully. Result: {json.dumps(result, default=str, indent=2)}")

def log_function_error(logger: logging.Logger, func_name: str, error: Exception, 
                    params: Optional[Dict[str, Any]] = None) -> None:
  """Log a function error with exception details.
  
  Args:
    logger: Logger instance to use
    func_name: Name of the function that failed
    error: Exception that was raised
    params: Optional dictionary of parameters that were used
  """
  error_msg = f"{func_name} failed with error: {str(error)}"
  if params:
      error_msg += f" | Params: {json.dumps(params, default=str)}"
  logger.error(error_msg, exc_info=True)