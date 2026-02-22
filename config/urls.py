"""IBM BAW documentation URLs and crawl configuration.

This module contains all target URLs for documentation crawling,
making it easy to update or add new documentation sources.
"""

# IBM Business Automation Workflow documentation base URL
BAW_DOCS_BASE = "https://www.ibm.com/docs/en/baw"

# Current BAW version being targeted
BAW_VERSION = "25.0.x"

# Seed URLs for documentation crawling
# These are the starting points for the web crawler
SEED_URLS = [
    f"{BAW_DOCS_BASE}/{BAW_VERSION}?topic=management-building-process-applications",
    f"{BAW_DOCS_BASE}/{BAW_VERSION}?topic=customizing-configuring-authoring-assistant",
    f"{BAW_DOCS_BASE}/{BAW_VERSION}?topic=customizing-configuring-workplace-assistant",
    f"{BAW_DOCS_BASE}/{BAW_VERSION}?topic=traditional-managing-projects",
    f"{BAW_DOCS_BASE}/{BAW_VERSION}?topic=glossary"
]

# Additional documentation sections (can be added as needed)
ADDITIONAL_SECTIONS = {
    "process_designer": f"{BAW_DOCS_BASE}/{BAW_VERSION}?topic=process-designer",
    "integration": f"{BAW_DOCS_BASE}/{BAW_VERSION}?topic=integration-services",
    "security": f"{BAW_DOCS_BASE}/{BAW_VERSION}?topic=security",
    "deployment": f"{BAW_DOCS_BASE}/{BAW_VERSION}?topic=deployment",
    "administration": f"{BAW_DOCS_BASE}/{BAW_VERSION}?topic=administration"
}

# URL patterns to include (regex patterns)
INCLUDE_PATTERNS = [
    r"https://www\.ibm\.com/docs/en/baw/.*",
]

# URL patterns to exclude (regex patterns)
EXCLUDE_PATTERNS = [
    r".*\.(pdf|zip|tar|gz)$",  # Binary files
    r".*/print/.*",  # Print versions
    r".*/download/.*",  # Download pages
]

# Allowed domains for crawling
ALLOWED_DOMAINS = [
    "www.ibm.com"
]

def get_all_seed_urls() -> list[str]:
    """Get all seed URLs including additional sections."""
    return SEED_URLS + list(ADDITIONAL_SECTIONS.values())

def get_seed_urls_by_category() -> dict[str, list[str]]:
    """Get seed URLs organized by category."""
    return {
        "core": SEED_URLS,
        "additional": list(ADDITIONAL_SECTIONS.values())
    }