"""Google Custom Search API implementation."""

import time
from typing import Dict, List, Optional

from src.search.search_types import SearchResult
from src.utils.logging_setup import get_logger

logger = get_logger(__name__)

# Try to import Google API client (optional dependency)
try:
    from googleapiclient.discovery import build
    from googleapiclient.errors import HttpError
    HAS_GOOGLE_API = True
except ImportError:
    HAS_GOOGLE_API = False


class GoogleSearchEngine:
    """
    Web search engine wrapper for Google Custom Search API.
    Requires API key and Custom Search Engine ID.
    Free tier: 100 queries/day
    """

    def __init__(self, config: Dict):
        """
        Initialize Google search engine.

        Args:
            config: Configuration dictionary with search settings

        Raises:
            ImportError: If google-api-python-client not installed
            ValueError: If API credentials missing
        """
        if not HAS_GOOGLE_API:
            raise ImportError(
                "google-api-python-client not installed. "
                "Install with: pip install google-api-python-client"
            )

        self.config = config['search']
        self.max_results = self.config.get('max_results_per_query', 5)

        # Get API credentials
        self.api_key = self.config.get('google_api_key')
        self.cse_id = self.config.get('google_cse_id')

        if not self.api_key or not self.cse_id:
            raise ValueError(
                "Google API credentials missing. Set:\n"
                "  - config['search']['google_api_key']\n"
                "  - config['search']['google_cse_id']\n"
                "Get credentials at: https://developers.google.com/custom-search/v1/overview"
            )

        # Build service
        self.service = build("customsearch", "v1", developerKey=self.api_key)

    def search(self, query: str, max_results: int = None) -> List[SearchResult]:
        """
        Search the web using Google Custom Search API.

        Args:
            query: Search query string
            max_results: Maximum results to return (uses config default if None)

        Returns:
            List of SearchResult objects

        Note:
            Returns empty list on errors rather than crashing.
            Google API limits: 10 results per request, 100 queries/day (free tier)
        """
        if max_results is None:
            max_results = self.max_results

        # Google API max 10 per request
        max_results = min(max_results, 10)

        logger.info(f"Searching Google for: '{query}' (max_results={max_results})")

        try:
            # Execute search
            result = self.service.cse().list(
                q=query,
                cx=self.cse_id,
                num=max_results
            ).execute()

            # Parse results
            results = []
            items = result.get('items', [])

            for item in items:
                results.append(SearchResult(
                    url=item.get('link', ''),
                    title=item.get('title', 'Untitled'),
                    snippet=item.get('snippet', '')
                ))

            logger.info(f"Found {len(results)} results from Google for '{query}'")
            return results

        except HttpError as e:
            error_details = e.error_details[0] if e.error_details else {}
            reason = error_details.get('reason', 'unknown')

            if 'rateLimitExceeded' in reason or 'quotaExceeded' in reason:
                logger.error(f"Google API quota exceeded for '{query}'")
            elif 'keyInvalid' in reason:
                logger.error(f"Invalid Google API key")
            else:
                logger.error(f"Google API error for '{query}': {e}")

            return []

        except Exception as e:
            logger.error(f"Unexpected error searching Google for '{query}': {type(e).__name__}: {e}")
            return []
