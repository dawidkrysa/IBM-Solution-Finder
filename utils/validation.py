"""Input validation utilities."""

import re
from typing import Optional
from config import Config


def sanitize_text(text: str) -> str:
    """
    Sanitize user input text.
    
    Args:
        text: Raw user input
        
    Returns:
        Sanitized text
    """
    if not text:
        return ""
    
    # Remove control characters
    text = re.sub(r'[\x00-\x1f\x7f-\x9f]', '', text)
    
    # Limit length
    text = text[:Config.MAX_INPUT_LENGTH]
    
    # Strip excessive whitespace
    text = ' '.join(text.split())
    
    return text


def validate_url(url: str) -> bool:
    """
    Validate URL format.
    
    Args:
        url: URL to validate
        
    Returns:
        True if valid
    """
    url_pattern = re.compile(
        r'^https?://'  # http:// or https://
        r'(?:(?:[A-Z0-9](?:[A-Z0-9-]{0,61}[A-Z0-9])?\.)+[A-Z]{2,6}\.?|'  # domain
        r'localhost|'  # localhost
        r'\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})'  # or IP
        r'(?::\d+)?'  # optional port
        r'(?:/?|[/?]\S+)$', re.IGNORECASE
    )
    return bool(url_pattern.match(url))


def sanitize_error_message(error: Exception) -> str:
    """
    Sanitize error messages to prevent information disclosure.
    
    Args:
        error: Exception object
        
    Returns:
        Safe error message
    """
    # Map of error types to user-friendly messages
    error_messages = {
        'ConnectionError': 'Unable to connect to service',
        'TimeoutError': 'Request timed out',
        'ValueError': 'Invalid input provided',
        'FileNotFoundError': 'Resource not found',
    }
    
    error_type = type(error).__name__
    return error_messages.get(error_type, 'An error occurred')