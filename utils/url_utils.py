"""
URL utilities for IBM documentation crawling.
Handles URL normalization, validation, and deduplication.
"""

from urllib.parse import urlparse, parse_qs, urlencode, urlunparse
from typing import Set, List
import re


def normalize_url(url: str) -> str:
    """
    Normalize IBM documentation URLs for proper deduplication.
    
    IBM docs use query parameters like ?topic=... which need special handling.
    This function:
    - Removes fragments (#anchors)
    - Sorts query parameters for consistent comparison
    - Lowercases the domain
    - Preserves the topic parameter structure
    
    Args:
        url: Raw URL string
        
    Returns:
        Normalized URL string
    """
    parsed = urlparse(url)
    
    # Parse query parameters
    query_params = parse_qs(parsed.query, keep_blank_values=True)
    
    # Sort parameters for consistent ordering
    sorted_params = sorted(query_params.items())
    normalized_query = urlencode(sorted_params, doseq=True)
    
    # Rebuild URL without fragment, with normalized query
    normalized = urlunparse((
        parsed.scheme,
        parsed.netloc.lower(),  # Lowercase domain
        parsed.path,
        parsed.params,
        normalized_query,
        ''  # Remove fragment
    ))
    
    return normalized


def is_valid_ibm_baw_url(url: str, version: str = "25.0.x") -> bool:
    """
    Check if URL is a valid IBM BAW documentation page.
    
    Args:
        url: URL to validate
        version: BAW version to filter for (default: 25.0.x)
        
    Returns:
        True if URL is valid IBM BAW documentation
    """
    # Must be IBM docs domain
    if not url.startswith("https://www.ibm.com/docs/"):
        return False
    
    # Must be BAW documentation
    if "/baw/" not in url:
        return False
    
    # Must match version pattern (handle both 25.0.x and 25.0.0 formats)
    # The 'x' in version means any digit or literal 'x'
    version_pattern = version.replace(".", r"\.").replace("x", r"[x\d]+")
    if not re.search(f"/baw/{version_pattern}", url):
        return False
    
    # Exclude non-documentation pages
    excluded_patterns = [
        "/contact",
        "/privacy",
        "/support/pages",
        "/legal",
        "/terms",
        "/accessibility"
    ]
    
    for pattern in excluded_patterns:
        if pattern in url.lower():
            return False
    
    return True


def extract_topic_from_url(url: str) -> str:
    """
    Extract the topic parameter from IBM documentation URL.
    
    Args:
        url: IBM documentation URL
        
    Returns:
        Topic string or empty string if not found
    """
    parsed = urlparse(url)
    query_params = parse_qs(parsed.query)
    
    # IBM docs use 'topic' parameter
    topic = query_params.get('topic', [''])[0]
    return topic


class URLTracker:
    """
    Track discovered and processed URLs to avoid duplicates and loops.
    """
    
    def __init__(self):
        self.discovered: Set[str] = set()
        self.processed: Set[str] = set()
        self.failed: Set[str] = set()
        
    def add_discovered(self, url: str) -> bool:
        """
        Add a newly discovered URL.
        
        Args:
            url: URL to add
            
        Returns:
            True if URL was new, False if already discovered
        """
        normalized = normalize_url(url)
        if normalized in self.discovered:
            return False
        self.discovered.add(normalized)
        return True
    
    def mark_processed(self, url: str):
        """Mark URL as successfully processed."""
        normalized = normalize_url(url)
        self.processed.add(normalized)
    
    def mark_failed(self, url: str):
        """Mark URL as failed to process."""
        normalized = normalize_url(url)
        self.failed.add(normalized)
    
    def is_processed(self, url: str) -> bool:
        """Check if URL has been processed."""
        normalized = normalize_url(url)
        return normalized in self.processed
    
    def get_pending(self) -> List[str]:
        """Get list of discovered but not yet processed URLs."""
        return list(self.discovered - self.processed - self.failed)
    
    def get_stats(self) -> dict:
        """Get crawling statistics."""
        return {
            "discovered": len(self.discovered),
            "processed": len(self.processed),
            "failed": len(self.failed),
            "pending": len(self.get_pending())
        }