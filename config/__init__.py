"""Configuration package for IBM Solution Finder.

This package provides centralized configuration management including:
- Application settings (settings.py)
- System prompts and templates (prompts.py)
- Documentation URLs (urls.py)
"""

from .settings import Settings as Config
from .prompts import (
    DEFAULT_SYSTEM_PROMPT,
    ANALYSIS_PROMPT_TEMPLATE,
    CLASSIFICATION_CATEGORIES,
    EXAMPLE_REQUIREMENTS
)
from .urls import (
    SEED_URLS,
    BAW_DOCS_BASE,
    BAW_VERSION,
    get_all_seed_urls,
    get_seed_urls_by_category
)

__all__ = [
    'Settings',
    'DEFAULT_SYSTEM_PROMPT',
    'ANALYSIS_PROMPT_TEMPLATE',
    'CLASSIFICATION_CATEGORIES',
    'EXAMPLE_REQUIREMENTS',
    'SEED_URLS',
    'BAW_DOCS_BASE',
    'BAW_VERSION',
    'get_all_seed_urls',
    'get_seed_urls_by_category'
]