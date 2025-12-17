"""Web search engine factory with multiple provider support."""

import time
from typing import Dict, List

from duckduckgo_search import DDGS

from src.search.search_types import SearchResult
from src.utils.logging_setup import get_logger

logger = get_logger(__name__)


class DuckDuckGoSearchEngine:
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


class SearchEngine:
    """
    Search engine factory that supports multiple providers.
    Supports: DuckDuckGo (no API key), Google Custom Search (requires API key).
    """

    def __init__(self, config: Dict):
        """
        Initialize search engine with configured provider.

        Args:
            config: Configuration dictionary with search settings

        The config['search']['provider'] determines behavior:
        - "duckduckgo": Use DuckDuckGo only
        - "google": Use Google Custom Search only
        - "auto" (default): Try DuckDuckGo first, fallback to Google if available
        """
        self.config = config['search']
        self.provider = self.config.get('provider', 'auto').lower()
        self.max_results = self.config.get('max_results_per_query', 5)

        # Initialize providers based on config
        self.ddg_engine = None
        self.google_engine = None

        if self.provider in ['duckduckgo', 'auto']:
            try:
                self.ddg_engine = DuckDuckGoSearchEngine(config)
                logger.info("DuckDuckGo search engine initialized")
            except Exception as e:
                logger.warning(f"Failed to initialize DuckDuckGo: {e}")

        if self.provider in ['google', 'auto']:
            try:
                from src.search.google_search_engine import GoogleSearchEngine
                self.google_engine = GoogleSearchEngine(config)
                logger.info("Google search engine initialized")
            except (ImportError, ValueError) as e:
                if self.provider == 'google':
                    # If explicitly requested Google, raise error
                    logger.error(f"Google search initialization failed: {e}")
                    raise
                # For auto mode, just log and continue
                logger.info(f"Google search not available: {e}")

        if not self.ddg_engine and not self.google_engine:
            raise ValueError(
                "No search providers available. "
                "Either configure Google API credentials or ensure DuckDuckGo is accessible."
            )

        # Log available providers
        providers = []
        if self.ddg_engine:
            providers.append("DuckDuckGo")
        if self.google_engine:
            providers.append("Google")
        logger.info(f"Search providers available: {', '.join(providers)} (mode: {self.provider})")

    def search(self, query: str, max_results: int = None) -> List[SearchResult]:
        """
        Search using configured provider(s).

        Args:
            query: Search query string
            max_results: Maximum results to return

        Returns:
            List of SearchResult objects

        Behavior based on provider:
        - "duckduckgo": Use DuckDuckGo only
        - "google": Use Google only
        - "auto": Try DuckDuckGo first, fallback to Google if DuckDuckGo returns empty
        """
        if max_results is None:
            max_results = self.max_results

        results = []

        # Try DuckDuckGo first (if available and not explicitly Google-only)
        if self.ddg_engine and self.provider != 'google':
            logger.info("Attempting search with DuckDuckGo...")
            results = self.ddg_engine.search(query, max_results)

            if results:
                logger.info(f"✓ DuckDuckGo returned {len(results)} results")
                return results
            elif self.provider == 'duckduckgo':
                # Explicitly DuckDuckGo only - don't try Google
                logger.warning("DuckDuckGo returned no results (no fallback configured)")
                return []

            logger.warning("DuckDuckGo returned no results, trying Google fallback...")

        # Try Google (if available)
        if self.google_engine:
            logger.info("Attempting search with Google Custom Search...")
            results = self.google_engine.search(query, max_results)

            if results:
                logger.info(f"✓ Google returned {len(results)} results")
            else:
                logger.warning("Google also returned no results")

        return results
