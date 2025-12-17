"""Web search engine implementation using DuckDuckGo."""

import time
from typing import Dict, List

from duckduckgo_search import DDGS

from src.search.search_types import SearchResult
from src.utils.logging_setup import get_logger

logger = get_logger(__name__)


class SearchEngine:
    """
    Web search engine wrapper for DuckDuckGo.
    No API key required.
    """

    def __init__(self, config: Dict):
        """
        Initialize search engine.

        Args:
            config: Configuration dictionary with search settings
        """
        self.config = config['search']
        self.max_results = self.config.get('max_results_per_query', 5)
        self.timeout = self.config.get('timeout_seconds', 10)
        self.user_agent = self.config.get(
            'user_agent',
            'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        )

    def search(self, query: str, max_results: int = None) -> List[SearchResult]:
        """
        Search the web using DuckDuckGo.

        Args:
            query: Search query string
            max_results: Maximum results to return (uses config default if None)

        Returns:
            List of SearchResult objects

        Note:
            Returns empty list on errors rather than crashing.
            Implements exponential backoff for rate limiting.
        """
        if max_results is None:
            max_results = self.max_results

        logger.info(f"Searching for: '{query}' (max_results={max_results})")

        # Retry logic with exponential backoff
        max_attempts = 3
        for attempt in range(max_attempts):
            try:
                results = []

                # Use DuckDuckGo search
                with DDGS() as ddgs:
                    search_results = ddgs.text(
                        keywords=query,
                        max_results=max_results,
                        safesearch='moderate'
                    )

                    for result in search_results:
                        results.append(SearchResult(
                            url=result.get('href', result.get('link', '')),
                            title=result.get('title', 'Untitled'),
                            snippet=result.get('body', result.get('description', ''))
                        ))

                logger.info(f"Found {len(results)} results for '{query}'")
                return results

            except Exception as e:
                wait_time = 2 ** attempt  # Exponential backoff: 1s, 2s, 4s
                logger.warning(
                    f"Search attempt {attempt + 1}/{max_attempts} failed for '{query}': {type(e).__name__}: {e}"
                )

                if attempt < max_attempts - 1:
                    logger.info(f"Retrying in {wait_time} seconds...")
                    time.sleep(wait_time)
                else:
                    logger.error(f"All search attempts failed for '{query}': {type(e).__name__}: {e}")
                    return []  # Return empty list instead of crashing

        return []
