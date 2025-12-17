"""Synthesizer using Claude to compare and synthesize findings from sources."""

import json
import time
from typing import Dict, List

import anthropic

from src.agent.prompts import SYNTHESIZE_PROMPT
from src.search.search_types import Contradiction, Fact, Synthesis
from src.utils.logging_setup import get_logger

logger = get_logger(__name__)


class Synthesizer:
    """
    Uses Claude to synthesize findings across multiple sources.

    AGENT DECISION POINT: How to reconcile conflicting information and identify gaps.
    """

    def __init__(self, config: Dict):
        """
        Initialize synthesizer.

        Args:
            config: Configuration dictionary with API settings
        """
        self.config = config
        self.client = anthropic.Anthropic(api_key=config['anthropic']['api_key'])
        self.model = config['anthropic']['model']
        self.max_tokens = config['anthropic'].get('max_tokens', 4000)
        self.temperature = config['anthropic'].get('temperature', 0.3)

    def synthesize(self, question: str, facts: List[Fact]) -> Synthesis:
        """
        Synthesize findings from multiple facts.

        Args:
            question: The original research question
            facts: List of extracted facts

        Returns:
            Synthesis object with agreements, contradictions, gaps, and answer

        Note:
            Falls back to simple summarization if synthesis fails.
        """
        logger.info(f"Synthesizing {len(facts)} facts")

        if not facts:
            logger.warning("No facts to synthesize")
            return Synthesis(
                agreements=[],
                contradictions=[],
                gaps=["No sources found with relevant information"],
                answer="Unable to answer the question due to lack of sources."
            )

        try:
            # Prepare facts as JSON for prompt
            facts_json = self._format_facts_for_prompt(facts)

            # Count unique sources
            num_sources = len(set(f.source_url for f in facts))

            # Format prompt
            prompt = SYNTHESIZE_PROMPT.format(
                question=question,
                num_sources=num_sources,
                facts_json=facts_json
            )

            # Call Claude
            response_text = self._call_claude(prompt)

            # Parse synthesis
            synthesis = self._parse_synthesis(response_text)

            logger.info("Successfully synthesized findings")
            return synthesis

        except Exception as e:
            logger.error(f"Synthesis failed: {e}")
            logger.info("Falling back to simple summarization")
            return self._fallback_synthesis(question, facts)

    def _format_facts_for_prompt(self, facts: List[Fact]) -> str:
        """
        Format facts as JSON string for the prompt.

        Args:
            facts: List of Fact objects

        Returns:
            JSON formatted string of facts
        """
        facts_data = []
        for fact in facts:
            facts_data.append({
                'claim': fact.claim,
                'caveat': fact.caveat,
                'confidence': fact.confidence,
                'source': fact.source_url
            })

        return json.dumps(facts_data, indent=2)

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

    def _parse_synthesis(self, response_text: str) -> Synthesis:
        """
        Parse synthesis from Claude's JSON response.

        Args:
            response_text: Raw response from Claude

        Returns:
            Synthesis object

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

            # Parse contradictions
            contradictions = []
            for c in data.get('contradictions', []):
                contradictions.append(Contradiction(
                    issue=c.get('issue', ''),
                    sources=c.get('sources', []),
                    explanation=c.get('explanation', '')
                ))

            # Create Synthesis object
            synthesis = Synthesis(
                agreements=data.get('agreements', []),
                contradictions=contradictions,
                gaps=data.get('gaps', []),
                answer=data.get('answer', '')
            )

            # Validate required fields
            if not synthesis.answer:
                raise ValueError("Missing 'answer' field in synthesis")

            return synthesis

        except json.JSONDecodeError as e:
            logger.error(f"Failed to parse JSON: {e}")
            logger.debug(f"Response text: {response_text}")
            raise ValueError(f"Invalid JSON response: {e}")

    def _fallback_synthesis(self, question: str, facts: List[Fact]) -> Synthesis:
        """
        Create a simple synthesis when Claude synthesis fails.

        Args:
            question: The research question
            facts: List of facts

        Returns:
            Basic Synthesis object
        """
        # Group facts by confidence
        high_conf = [f for f in facts if f.confidence == 'high']

        # Simple answer from high confidence facts
        if high_conf:
            answer = f"Based on {len(high_conf)} high-confidence sources: " + \
                     " ".join([f.claim for f in high_conf[:3]])
        else:
            answer = "Multiple sources discuss this topic, but confidence levels vary. " + \
                     f"Key points include: {facts[0].claim if facts else 'No clear consensus.'}"

        return Synthesis(
            agreements=["Multiple sources found"],
            contradictions=[],
            gaps=["Detailed analysis unavailable due to synthesis error"],
            answer=answer
        )
