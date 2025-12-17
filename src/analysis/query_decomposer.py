"""Query decomposer using Claude to break down complex questions."""

import json
import time
from typing import Dict, List

import anthropic

from src.agent.prompts import DECOMPOSE_PROMPT
from src.utils.logging_setup import get_logger

logger = get_logger(__name__)


class QueryDecomposer:
    """
    Uses Claude to decompose complex research questions into searchable sub-queries.

    AGENT DECISION POINT: How to break down questions for optimal coverage.
    """

    def __init__(self, config: Dict):
        """
        Initialize query decomposer.

        Args:
            config: Configuration dictionary with API settings
        """
        self.config = config
        self.client = anthropic.Anthropic(api_key=config['anthropic']['api_key'])
        self.model = config['anthropic']['model']
        self.max_tokens = config['anthropic'].get('max_tokens', 4000)
        self.temperature = config['anthropic'].get('temperature', 0.3)

        self.min_queries = config['agent'].get('min_subqueries', 3)
        self.max_queries = config['agent'].get('max_subqueries', 5)

    def decompose(self, question: str) -> List[str]:
        """
        Decompose a complex question into 3-5 searchable sub-queries.

        Args:
            question: The original research question

        Returns:
            List of sub-query strings

        Note:
            Falls back to returning [original_question] if decomposition fails.
            Implements retry logic for rate limits.
        """
        logger.info(f"Decomposing question: '{question}'")

        # Format prompt
        prompt = DECOMPOSE_PROMPT.format(question=question)

        # Call Claude with retry logic
        try:
            response_text = self._call_claude(prompt)

            # Parse JSON response
            sub_queries = self._parse_queries(response_text)

            # Validate count
            if len(sub_queries) < self.min_queries:
                logger.warning(
                    f"Only got {len(sub_queries)} sub-queries, expected at least {self.min_queries}"
                )
                # Use original question as fallback
                return [question]

            if len(sub_queries) > self.max_queries:
                logger.info(f"Truncating to {self.max_queries} sub-queries")
                sub_queries = sub_queries[:self.max_queries]

            logger.info(f"Successfully decomposed into {len(sub_queries)} sub-queries")
            return sub_queries

        except Exception as e:
            logger.error(f"Query decomposition failed: {e}")
            logger.info("Falling back to original question")
            return [question]

    def _call_claude(self, prompt: str, max_retries: int = 3) -> str:
        """
        Call Claude API with retry logic.

        Args:
            prompt: The prompt to send
            max_retries: Maximum retry attempts

        Returns:
            Response text from Claude

        Raises:
            Exception: If all retries fail
        """
        for attempt in range(max_retries):
            try:
                response = self.client.messages.create(
                    model=self.model,
                    max_tokens=self.max_tokens,
                    temperature=self.temperature,
                    messages=[
                        {"role": "user", "content": prompt}
                    ]
                )

                return response.content[0].text

            except anthropic.RateLimitError as e:
                if attempt < max_retries - 1:
                    wait_time = 2 ** attempt  # Exponential backoff
                    logger.warning(f"Rate limit hit, retrying in {wait_time}s...")
                    time.sleep(wait_time)
                else:
                    logger.error("Rate limit exceeded, no more retries")
                    raise

            except anthropic.APIError as e:
                logger.error(f"Claude API error: {e}")
                raise

    def _parse_queries(self, response_text: str) -> List[str]:
        """
        Parse sub-queries from Claude's JSON response.

        Args:
            response_text: Raw response from Claude

        Returns:
            List of query strings

        Raises:
            ValueError: If response cannot be parsed
        """
        try:
            # Try to find JSON array in response
            # Sometimes Claude adds explanation text, so extract JSON
            start_idx = response_text.find('[')
            end_idx = response_text.rfind(']') + 1

            if start_idx == -1 or end_idx == 0:
                raise ValueError("No JSON array found in response")

            json_str = response_text[start_idx:end_idx]
            queries = json.loads(json_str)

            if not isinstance(queries, list):
                raise ValueError("Expected JSON array")

            # Filter out empty queries
            queries = [q.strip() for q in queries if q and q.strip()]

            return queries

        except json.JSONDecodeError as e:
            logger.error(f"Failed to parse JSON: {e}")
            logger.debug(f"Response text: {response_text}")
            raise ValueError(f"Invalid JSON response: {e}")
