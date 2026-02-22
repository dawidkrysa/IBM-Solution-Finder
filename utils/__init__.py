"""Utility modules for IBM Solution Finder.

This package provides core utilities for:
- Ollama AI model interaction and RAG orchestration
- Web crawling with Selenium for JavaScript-rendered content
- URL normalization and validation
- Input validation and sanitization
- Logging configuration
"""

# Ollama and RAG utilities
from .ollama_utils import (
    get_available_models,
    generate_response,
    ingest_knowledge,
    get_context
)

# Web crawling
from .selenium_crawler import SeleniumCrawler

# URL utilities
from .url_utils import (
    normalize_url,
    is_valid_ibm_baw_url,
    URLTracker
)

# Validation
from .validation import (
    sanitize_text,
    sanitize_error_message
)

# Logging
from .logging_config import setup_logging

__all__ = [
    # Ollama utilities
    'get_available_models',
    'generate_response',
    'ingest_knowledge',
    'get_context',
    # Crawler
    'SeleniumCrawler',
    # URL utilities
    'normalize_url',
    'is_valid_ibm_baw_url',
    'URLTracker',
    # Validation
    'sanitize_text',
    'sanitize_error_message',
    # Logging
    'setup_logging',
]