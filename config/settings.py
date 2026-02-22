"""Application settings and configuration.

This module centralizes all application configuration, making it easy to manage
environment-specific settings and maintain consistency across the application.
"""

import os
from typing import Optional
from pathlib import Path


class Settings:
    """Application settings loaded from environment variables."""
    
    # Application
    APP_VERSION: str = os.getenv('APP_VERSION', '1.0.0')
    APP_ENV: str = os.getenv('APP_ENV', 'development')
    DEBUG: bool = os.getenv('DEBUG', 'false').lower() == 'true'
    
    # Ollama
    OLLAMA_BASE_URL: str = os.getenv('OLLAMA_BASE_URL', 'http://ollama-engine:11434')
    OLLAMA_TIMEOUT: int = int(os.getenv('OLLAMA_TIMEOUT', '10'))
    
    # Database
    CHROMA_DB_PATH: str = os.getenv('CHROMA_DB_PATH', '/app/chroma_db')
    EMBEDDING_MODEL: str = os.getenv('EMBEDDING_MODEL', 'all-MiniLM-L6-v2')
    
    # Crawler
    CRAWLER_MAX_DEPTH: int = int(os.getenv('CRAWLER_MAX_DEPTH', '0'))
    CRAWLER_MAX_PAGES: int = int(os.getenv('CRAWLER_MAX_PAGES', '100'))
    CRAWLER_DELAY: float = float(os.getenv('CRAWLER_DELAY', '2.0'))
    CRAWLER_TIMEOUT: int = int(os.getenv('CRAWLER_TIMEOUT', '30'))
    CRAWLER_USER_AGENT: str = os.getenv(
        'CRAWLER_USER_AGENT',
        f'IBMSolutionFinder/{APP_VERSION}'
    )
    
    # Text Processing
    CHUNK_SIZE: int = int(os.getenv('CHUNK_SIZE', '1000'))
    CHUNK_OVERLAP: int = int(os.getenv('CHUNK_OVERLAP', '100'))
    RETRIEVAL_COUNT: int = int(os.getenv('RETRIEVAL_COUNT', '3'))
    MAX_INPUT_LENGTH: int = int(os.getenv('MAX_INPUT_LENGTH', '5000'))
    
    # Security
    CHROME_NO_SANDBOX: bool = os.getenv('CHROME_NO_SANDBOX', 'false').lower() == 'true'
    
    # BAW
    BAW_VERSION: str = os.getenv('BAW_VERSION', '25.0.x')
    
    # Logging
    LOG_LEVEL: str = os.getenv('LOG_LEVEL', 'INFO')
    LOG_FILE: str = os.getenv('LOG_FILE', '/app/logs/app.log')
    
    @classmethod
    def validate(cls) -> None:
        """Validate configuration values."""
        if cls.CRAWLER_MAX_PAGES > 500:
            raise ValueError("CRAWLER_MAX_PAGES cannot exceed 500")
        
        if cls.CRAWLER_DELAY < 1.0:
            raise ValueError("CRAWLER_DELAY must be at least 1.0 seconds")
        
        if cls.MAX_INPUT_LENGTH > 10000:
            raise ValueError("MAX_INPUT_LENGTH cannot exceed 10000")
    
    @classmethod
    def get_all(cls) -> dict:
        """Get all configuration as a dictionary."""
        return {
            key: getattr(cls, key)
            for key in dir(cls)
            if not key.startswith('_') and key.isupper()
        }


# Validate on import
Settings.validate()