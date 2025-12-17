"""Fact extractor using Claude to extract key information from sources."""

import json
import time
from typing import Dict, List

import anthropic

from src.agent.prompts import EXTRACT_PROMPT
from src.search.search_types import Fact, Source
from src.utils.logging_setup import get_logger

logger = get_logger(__name__)


class FactExtractor:
    """
    Uses Claude to extract key facts from source content.

    AGENT DECISION POINT: What facts are relevant and reliable for the research question.
    """

    def __init__(self, config: Dict):
        """
        Initialize fact extractor.

        Args:
            config: Configuration dictionary with API settings
        """
        self.config = config
        self.client = anthropic.Anthropic(api_key=config['anthropic']['api_key'])
        self.model = config['anthropic']['model']
        self.max_tokens = config['anthropic'].get('max_tokens', 4000)
        self.temperature = config['anthropic'].get('temperature', 0.3)

        self.facts_per_source = config['agent'].get('facts_per_source', 5)

    def extract_facts(self, sources: List[Source], question: str) -> List[Fact]:
        """
        Extract key facts from multiple sources.

        Args:
            sources: List of Source objects with content
            question: The original research question (for relevance)

        Returns:
            List of Fact objects with source attribution

        Note:
            Continues with partial results if some extractions fail.
            Skips sources without content.
        """
        logger.info(f"Extracting facts from {len(sources)} sources")

        all_facts = []

        for source in sources:
            if not source.content:
                logger.warning(f"Skipping source with no content: {source.url}")
                continue

            try:
                facts = self._extract_from_source(source, question)
                all_facts.extend(facts)
                logger.info(f"Extracted {len(facts)} facts from {source.url}")

            except Exception as e:
                logger.error(f"Failed to extract facts from {source.url}: {e}")
                # Continue with other sources instead of failing completely

        logger.info(f"Extracted total of {len(all_facts)} facts from all sources")
        return all_facts

    def _extract_from_source(self, source: Source, question: str) -> List[Fact]:
        """
        Extract facts from a single source.

        Args:
            source: Source object
            question: Research question

        Returns:
            List of Fact objects
        """
        # Format prompt
        prompt = EXTRACT_PROMPT.format(
            question=question,
            url=source.url,
            content=source.content[:10000]  # Limit content length for API
        )

        # Call Claude
        response_text = self._call_claude(prompt)

        # Parse facts
        facts = self._parse_facts(response_text, source.url)

        return facts

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
                    wait_time = 2 ** attempt
                    logger.warning(f"Rate limit hit, retrying in {wait_time}s...")
                    time.sleep(wait_time)
                else:
                    logger.error("Rate limit exceeded, no more retries")
                    raise

            except anthropic.APIError as e:
                logger.error(f"Claude API error: {e}")
                raise

    def _parse_facts(self, response_text: str, source_url: str) -> List[Fact]:
        """
        Parse facts from Claude's JSON response.

        Args:
            response_text: Raw response from Claude
            source_url: URL of the source (for attribution)

        Returns:
            List of Fact objects

        Raises:
            ValueError: If response cannot be parsed
        """
        try:
            # Extract JSON from response
            start_idx = response_text.find('{')
            end_idx = response_text.rfind('}') + 1

            if start_idx == -1 or end_idx == 0:
                raise ValueError("No JSON object found in response")

            json_str = response_text[start_idx:end_idx]
            data = json.loads(json_str)

            if 'facts' not in data:
                raise ValueError("No 'facts' key in response")

            facts_data = data['facts']
            if not isinstance(facts_data, list):
                raise ValueError("'facts' should be a list")

            # Convert to Fact objects
            facts = []
            for fact_dict in facts_data:
                try:
                    fact = Fact(
                        claim=fact_dict.get('claim', ''),
                        caveat=fact_dict.get('caveat'),
                        confidence=fact_dict.get('confidence', 'medium').lower(),
                        source_url=source_url
                    )

                    # Validate confidence
                    if fact.confidence not in ['high', 'medium', 'low']:
                        logger.warning(
                            f"Invalid confidence '{fact.confidence}', defaulting to 'medium'"
                        )
                        fact.confidence = 'medium'

                    if fact.claim:  # Only add if we have a claim
                        facts.append(fact)

                except Exception as e:
                    logger.warning(f"Failed to parse fact: {e}")
                    continue

            return facts

        except json.JSONDecodeError as e:
            logger.error(f"Failed to parse JSON: {e}")
            logger.debug(f"Response text: {response_text}")
            raise ValueError(f"Invalid JSON response: {e}")
