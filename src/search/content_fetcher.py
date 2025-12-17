"""Content fetcher for extracting clean text from web pages."""

import time
from typing import Dict, Optional

import requests
import trafilatura

from src.utils.logging_setup import get_logger

logger = get_logger(__name__)


class ContentFetcher:
    """
    Fetches web page content and extracts clean text.
    Uses trafilatura for robust HTML extraction.
    """

    def __init__(self, config: Dict):
        """
        Initialize content fetcher.

        Args:
            config: Configuration dictionary with fetching settings
        """
        self.config = config['fetching']
        self.max_length = self.config.get('max_content_length', 5000)  # words
        self.timeout = self.config.get('timeout_seconds', 10)
        self.retry_attempts = self.config.get('retry_attempts', 2)
        self.user_agent = config['search'].get(
            'user_agent',
            'Mozilla/5.0 (compatible; ResearchAssistant/1.0)'
        )

    def fetch_content(self, url: str) -> Optional[str]:
        """
        Fetch and extract clean text content from a URL.

        Args:
            url: Web page URL

        Returns:
            Clean text content (limited to max_length words), or None if failed

        Note:
            Returns None on failures (404, 403, timeout, etc.) rather than crashing.
            Logs warnings for debugging but doesn't stop the research process.
        """
        logger.info(f"Fetching content from: {url}")

        for attempt in range(self.retry_attempts):
            try:
                # Fetch HTML
                response = requests.get(
                    url,
                    timeout=self.timeout,
                    headers={'User-Agent': self.user_agent},
                    allow_redirects=True
                )
                response.raise_for_status()

                # Extract clean text using trafilatura
                content = trafilatura.extract(
                    response.content,
                    include_comments=False,
                    include_tables=True,
                    no_fallback=False
                )

                if not content:
                    logger.warning(f"No content extracted from {url}")
                    return None

                # Limit to max_length words
                words = content.split()
                if len(words) > self.max_length:
                    logger.info(
                        f"Truncating content from {len(words)} to {self.max_length} words"
                    )
                    content = ' '.join(words[:self.max_length])

                logger.info(f"Successfully fetched {len(content)} characters from {url}")
                return content

            except requests.HTTPError as e:
                status_code = e.response.status_code

                if status_code == 404:
                    logger.warning(f"Page not found (404): {url}")
                    return None
                elif status_code == 403:
                    logger.warning(f"Access denied (403), likely paywall: {url}")
                    return None
                elif status_code >= 500:
                    # Server error - might be temporary, retry
                    logger.warning(f"Server error ({status_code}): {url}")
                    if attempt < self.retry_attempts - 1:
                        time.sleep(2 ** attempt)  # Exponential backoff
                        continue
                else:
                    logger.warning(f"HTTP error ({status_code}): {url}")
                    return None

            except requests.Timeout:
                logger.warning(f"Timeout fetching {url}")
                if attempt < self.retry_attempts - 1:
                    logger.info(f"Retrying... (attempt {attempt + 2}/{self.retry_attempts})")
                    time.sleep(1)
                    continue
                return None

            except requests.RequestException as e:
                logger.warning(f"Request error for {url}: {e}")
                return None

            except Exception as e:
                logger.error(f"Unexpected error fetching {url}: {e}")
                return None

        logger.warning(f"All fetch attempts failed for {url}")
        return None
