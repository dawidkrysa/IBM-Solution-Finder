"""Application configuration - Backward compatibility wrapper.

This module provides backward compatibility by re-exporting the Settings class
from the config package as Config. New code should import directly from config.settings.
"""

from config.settings import Settings as Config

# Re-export for backward compatibility
__all__ = ['Config']