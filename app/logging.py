"""
Logging configuration for the CRE Chatbot application.
"""
import logging
import os
from logging.handlers import RotatingFileHandler
from .config import LOG_LEVEL, LOG_FORMAT, LOG_FILE

def setup_logging():
    """Set up logging configuration for the application."""
    # Create logs directory if it doesn't exist
    os.makedirs('logs', exist_ok=True)
    
    # Set up root logger
    logger = logging.getLogger()
    logger.setLevel(LOG_LEVEL)
    
    # Create formatters and handlers
    formatter = logging.Formatter(LOG_FORMAT)
    
    # Console Handler
    console_handler = logging.StreamHandler()
    console_handler.setFormatter(formatter)
    logger.addHandler(console_handler)
    
    # File Handler
    file_handler = RotatingFileHandler(
        LOG_FILE,
        maxBytes=10485760,  # 10MB
        backupCount=5
    )
    file_handler.setFormatter(formatter)
    logger.addHandler(file_handler)
    
    # Create separate loggers for different components
    loggers = {
        'api': setup_component_logger('api'),
        'pdf': setup_component_logger('pdf'),
        'rag': setup_component_logger('rag'),
        'app': setup_component_logger('app')
    }
    
    return loggers

def setup_component_logger(name):
    """Set up a logger for a specific component."""
    logger = logging.getLogger(name)
    logger.setLevel(LOG_LEVEL)
    
    # Create component-specific log file
    handler = RotatingFileHandler(
        f'logs/{name}.log',
        maxBytes=10485760,  # 10MB
        backupCount=3
    )
    handler.setFormatter(logging.Formatter(LOG_FORMAT))
    logger.addHandler(handler)
    
    return logger
