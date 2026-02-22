"""
Selenium-based crawler for JavaScript-rendered IBM documentation.
"""

from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, WebDriverException
from bs4 import BeautifulSoup
from typing import List, Optional, Callable
from urllib.parse import urljoin
import time
import logging
from utils.url_utils import normalize_url, is_valid_ibm_baw_url, URLTracker

logger = logging.getLogger(__name__)


class SeleniumCrawler:
    """
    Selenium-based crawler that can handle JavaScript-rendered content.
    """
    
    def __init__(
        self,
        max_depth: int = 2,
        max_pages: int = 100,
        delay: float = 2.0,
        page_load_timeout: int = 30
    ):
        """
        Initialize the Selenium crawler.
        
        Args:
            max_depth: Maximum crawl depth
            max_pages: Maximum number of pages to crawl
            delay: Delay between requests in seconds
            page_load_timeout: Timeout for page load in seconds
        """
        self.max_depth = max_depth
        self.max_pages = max_pages
        self.delay = delay
        self.page_load_timeout = page_load_timeout
        self.url_tracker = URLTracker()
        self.driver = None
        
    def _init_driver(self):
        """Initialize Chrome driver with appropriate options."""
        chrome_options = Options()
        chrome_options.add_argument('--headless')
        chrome_options.add_argument('--no-sandbox')
        chrome_options.add_argument('--disable-dev-shm-usage')
        chrome_options.add_argument('--disable-gpu')
        chrome_options.add_argument('--window-size=1920,1080')
        chrome_options.add_argument('--user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36')
        
        try:
            self.driver = webdriver.Chrome(options=chrome_options)
            self.driver.set_page_load_timeout(self.page_load_timeout)
            logger.info("Chrome driver initialized successfully")
        except Exception as e:
            logger.error(f"Failed to initialize Chrome driver: {e}")
            raise
    
    def _close_driver(self):
        """Close the Chrome driver."""
        if self.driver:
            try:
                self.driver.quit()
                logger.info("Chrome driver closed")
            except Exception as e:
                logger.error(f"Error closing driver: {e}")
    
    def _extract_content(self, url: str) -> Optional[str]:
        """
        Extract content from a page using Selenium.
        
        Args:
            url: URL to extract content from
            
        Returns:
            Extracted text content or None if failed
        """
        try:
            self.driver.get(url)
            
            # Wait for content to load (adjust selector based on IBM's structure)
            try:
                WebDriverWait(self.driver, 10).until(
                    EC.presence_of_element_located((By.TAG_NAME, "body"))
                )
                # Give extra time for JavaScript to render
                time.sleep(2)
            except TimeoutException:
                logger.warning(f"Timeout waiting for content on {url}")
            
            # Get page source after JavaScript execution
            page_source = self.driver.page_source
            
            # Parse with BeautifulSoup
            soup = BeautifulSoup(page_source, 'html.parser')
            
            # Remove non-content elements
            for element in soup(['script', 'style', 'nav', 'footer', 'header', 'aside', 'iframe']):
                element.decompose()
            
            # Extract text
            text = soup.get_text(separator=' ', strip=True)
            text = ' '.join(text.split())  # Clean whitespace
            
            return text
            
        except Exception as e:
            logger.error(f"Error extracting content from {url}: {e}")
            return None
    
    def _extract_links(self, url: str) -> List[str]:
        """
        Extract links from current page.
        
        Args:
            url: Base URL for resolving relative links
            
        Returns:
            List of valid absolute URLs
        """
        try:
            links = []
            elements = self.driver.find_elements(By.TAG_NAME, "a")
            
            for element in elements:
                try:
                    href = element.get_attribute('href')
                    if href:
                        absolute_url = urljoin(url, href)
                        normalized = normalize_url(absolute_url)
                        
                        if is_valid_ibm_baw_url(normalized):
                            links.append(normalized)
                except Exception:
                    continue
            
            # Remove duplicates
            return list(set(links))
            
        except Exception as e:
            logger.error(f"Error extracting links from {url}: {e}")
            return []
    
    def crawl(
        self,
        seed_urls: List[str],
        progress_callback: Optional[Callable] = None
    ) -> List[dict]:
        """
        Crawl IBM documentation using Selenium.
        
        Args:
            seed_urls: List of starting URLs
            progress_callback: Optional callback for progress updates
            
        Returns:
            List of documents with content and metadata
        """
        documents = []
        
        try:
            # Initialize driver
            self._init_driver()
            
            # Initialize queue
            queue = [(url, 0) for url in seed_urls]
            
            for url, depth in queue:
                # Check limits - stop if we've discovered enough pages
                if len(self.url_tracker.discovered) >= self.max_pages:
                    logger.info(f"Reached max pages limit: {self.max_pages}")
                    break
                
                if depth > self.max_depth:
                    continue
                
                # Skip if already processed
                if self.url_tracker.is_processed(url):
                    continue
                
                # Validate URL
                if not is_valid_ibm_baw_url(url):
                    logger.debug(f"Skipping invalid URL: {url}")
                    continue
                
                # Add to discovered
                if not self.url_tracker.add_discovered(url):
                    continue
                
                # Progress callback
                if progress_callback:
                    stats = self.url_tracker.get_stats()
                    progress_callback(stats)
                
                # Fetch and process page
                try:
                    # Double-check we haven't exceeded limit
                    if len(self.url_tracker.processed) >= self.max_pages:
                        logger.info(f"Stopping: already processed {self.max_pages} pages")
                        break
                    
                    logger.info(f"Crawling [{depth}]: {url}")
                    
                    # Extract content
                    content = self._extract_content(url)
                    
                    # Store document
                    if content and len(content.strip()) > 100:
                        documents.append({
                            'content': content,
                            'metadata': {
                                'source': url,
                                'depth': depth
                            }
                        })
                        
                        self.url_tracker.mark_processed(url)
                        logger.info(f"✓ Processed: {url} ({len(content)} chars)")
                        
                        # Extract and queue new links (only if under limit)
                        if depth < self.max_depth and len(self.url_tracker.discovered) < self.max_pages:
                            new_links = self._extract_links(url)
                            links_to_add = []
                            for link in new_links:
                                if not self.url_tracker.is_processed(link):
                                    # Stop adding if we're at the limit
                                    if len(self.url_tracker.discovered) + len(links_to_add) >= self.max_pages:
                                        break
                                    links_to_add.append((link, depth + 1))
                            
                            queue.extend(links_to_add)
                            logger.info(f"  Found {len(new_links)} links, added {len(links_to_add)} to queue")
                    else:
                        logger.warning(f"Insufficient content ({len(content) if content else 0} chars): {url}")
                        self.url_tracker.mark_failed(url)
                    
                    # Delay between requests
                    time.sleep(self.delay)
                    
                except Exception as e:
                    logger.error(f"Error processing {url}: {e}")
                    self.url_tracker.mark_failed(url)
            
            # Final stats
            stats = self.url_tracker.get_stats()
            logger.info(f"Crawl complete: {stats}")
            
        finally:
            # Always close driver
            self._close_driver()
        
        return documents
    
    def get_stats(self) -> dict:
        """Get crawling statistics."""
        return self.url_tracker.get_stats()