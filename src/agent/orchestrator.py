"""Research orchestrator that coordinates the complete workflow."""

from datetime import datetime
from pathlib import Path
from typing import Dict

from src.analysis.fact_extractor import FactExtractor
from src.analysis.query_decomposer import QueryDecomposer
from src.analysis.synthesizer import Synthesizer
from src.search.content_fetcher import ContentFetcher
from src.search.search_engine import SearchEngine
from src.search.search_types import ResearchReport, Source
from src.utils.logging_setup import get_logger

logger = get_logger(__name__)


class ResearchOrchestrator:
    """
    Coordinates the complete research workflow.

    This is the main agent that orchestrates all components to produce a research report.
    """

    def __init__(self, config: Dict):
        """
        Initialize research orchestrator.

        Args:
            config: Configuration dictionary
        """
        self.config = config

        # Initialize all components
        logger.info("Initializing research components...")
        self.decomposer = QueryDecomposer(config)
        self.search_engine = SearchEngine(config)
        self.fetcher = ContentFetcher(config)
        self.extractor = FactExtractor(config)
        self.synthesizer = Synthesizer(config)

        # Output settings
        self.report_dir = Path(config['output']['report_dir'])
        self.report_dir.mkdir(parents=True, exist_ok=True)
        self.save_intermediate = config['output'].get('save_intermediate', False)

    def research(self, question: str) -> ResearchReport:
        """
        Conduct complete research for a question.

        This is the main workflow:
        1. Decompose question into sub-queries (AGENT DECISION POINT)
        2. Search for each sub-query
        3. Fetch content from search results
        4. Extract facts from sources (AGENT DECISION POINT)
        5. Synthesize findings (AGENT DECISION POINT)
        6. Generate report

        Args:
            question: The research question

        Returns:
            Complete ResearchReport object

        Raises:
            ValueError: If no sources are found
        """
        logger.info(f"Starting research for: '{question}'")

        # Step 1: Decompose question into sub-queries
        # AGENT DECISION POINT: How to break down the question for optimal coverage
        logger.info("Step 1: Decomposing question into sub-queries...")
        try:
            sub_queries = self.decomposer.decompose(question)
            logger.info(f"Generated {len(sub_queries)} sub-queries: {sub_queries}")
        except Exception as e:
            logger.error(f"Decomposition failed: {e}")
            # Fallback to original question
            sub_queries = [question]

        # Step 2 & 3: Search and fetch content for each sub-query
        # AGENT DECISION POINT: Search strategy per query
        logger.info("Step 2-3: Searching and fetching content...")
        all_sources = self._search_and_fetch(sub_queries)

        if not all_sources:
            raise ValueError(
                "No sources found or all content fetches failed. "
                "Check your internet connection or try a different question."
            )

        logger.info(f"Successfully gathered {len(all_sources)} sources")

        # Save intermediate results if configured
        if self.save_intermediate:
            self._save_sources(question, all_sources)

        # Step 4: Extract facts from all sources
        # AGENT DECISION POINT: What facts are relevant and reliable
        logger.info("Step 4: Extracting key facts from sources...")
        facts = self.extractor.extract_facts(all_sources, question)
        logger.info(f"Extracted {len(facts)} facts")

        if not facts:
            logger.warning("No facts extracted, research quality may be poor")

        # Step 5: Synthesize findings
        # AGENT DECISION POINT: How to reconcile conflicts and identify gaps
        logger.info("Step 5: Synthesizing findings...")
        synthesis = self.synthesizer.synthesize(question, facts)

        # Step 6: Create report
        logger.info("Step 6: Generating report...")
        report = ResearchReport(
            question=question,
            sub_queries=sub_queries,
            sources=all_sources,
            facts=facts,
            synthesis=synthesis,
            timestamp=datetime.now()
        )

        # Save report
        self._save_report(report)

        logger.info("Research completed successfully!")
        return report

    def _search_and_fetch(self, queries: list[str]) -> list[Source]:
        """
        Search for and fetch content for multiple queries.

        Args:
            queries: List of search queries

        Returns:
            List of Source objects with content

        Note:
            Continues with partial results if some searches/fetches fail.
        """
        all_sources = []

        for query in queries:
            logger.info(f"Searching for: '{query}'")

            # Search
            search_results = self.search_engine.search(query)

            if not search_results:
                logger.warning(f"No search results for: '{query}'")
                continue

            # Fetch content from each result
            for result in search_results:
                content = self.fetcher.fetch_content(result.url)

                if content:
                    source = Source(
                        url=result.url,
                        title=result.title,
                        content=content,
                        fetch_time=datetime.now()
                    )
                    all_sources.append(source)
                else:
                    logger.warning(f"Failed to fetch content from: {result.url}")

        return all_sources

    def _save_report(self, report: ResearchReport) -> Path:
        """
        Save report to markdown file.

        Args:
            report: ResearchReport object

        Returns:
            Path to saved report file
        """
        # Generate filename with timestamp
        timestamp = report.timestamp.strftime('%Y%m%d_%H%M%S')
        filename = f"research_report_{timestamp}.md"
        filepath = self.report_dir / filename

        # Generate markdown
        markdown = report.to_markdown()

        # Save to file
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(markdown)

        logger.info(f"Report saved to: {filepath}")
        return filepath

    def _save_sources(self, question: str, sources: list[Source]) -> None:
        """
        Save intermediate source data (for debugging).

        Args:
            question: Research question
            sources: List of sources
        """
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        filename = f"sources_{timestamp}.txt"
        filepath = self.report_dir / filename

        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(f"Sources for: {question}\n")
            f.write(f"Collected at: {datetime.now()}\n")
            f.write("=" * 80 + "\n\n")

            for idx, source in enumerate(sources, 1):
                f.write(f"Source {idx}: {source.title}\n")
                f.write(f"URL: {source.url}\n")
                f.write(f"Content length: {len(source.content)} characters\n")
                f.write("-" * 80 + "\n")
                f.write(source.content[:1000] + "...\n\n")

        logger.info(f"Sources saved to: {filepath}")
