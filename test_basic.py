"""Basic test to verify imports and structure."""

import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent / "src"))

print("Testing imports...")

# Test all imports
try:
    from src.search.search_types import SearchResult, Source, Fact, Synthesis, ResearchReport
    print("✓ search_types")

    from src.search.search_engine import SearchEngine
    print("✓ search_engine")

    from src.search.content_fetcher import ContentFetcher
    print("✓ content_fetcher")

    from src.agent.prompts import DECOMPOSE_PROMPT, EXTRACT_PROMPT, SYNTHESIZE_PROMPT
    print("✓ prompts")

    from src.analysis.query_decomposer import QueryDecomposer
    print("✓ query_decomposer")

    from src.analysis.fact_extractor import FactExtractor
    print("✓ fact_extractor")

    from src.analysis.synthesizer import Synthesizer
    print("✓ synthesizer")

    from src.agent.orchestrator import ResearchOrchestrator
    print("✓ orchestrator")

    from src.utils.config_loader import load_config
    print("✓ config_loader")

    from src.utils.logging_setup import setup_logging, get_logger
    print("✓ logging_setup")

    print("\n✅ All imports successful!")

    # Test data model creation
    print("\nTesting data models...")
    from datetime import datetime

    search_result = SearchResult(
        url="https://example.com",
        title="Test",
        snippet="Test snippet"
    )
    print("✓ SearchResult created")

    source = Source(
        url="https://example.com",
        title="Test",
        content="Test content",
        fetch_time=datetime.now()
    )
    print("✓ Source created")

    fact = Fact(
        claim="Test claim",
        caveat=None,
        confidence="high",
        source_url="https://example.com"
    )
    print("✓ Fact created")

    print("\n✅ All tests passed!")
    print("\nTo run the full application:")
    print("1. Set ANTHROPIC_API_KEY environment variable")
    print("2. Run: poetry run streamlit run src/main.py")

except ImportError as e:
    print(f"\n❌ Import error: {e}")
    sys.exit(1)
except Exception as e:
    print(f"\n❌ Error: {e}")
    sys.exit(1)
