"""Streamlit web interface for the Research Assistant."""

import sys
from pathlib import Path
from datetime import datetime

# Add project root to Python path for imports
project_root = Path(__file__).parent.parent
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))

import streamlit as st

from src.agent.orchestrator import ResearchOrchestrator
from src.utils.config_loader import load_config
from src.utils.logging_setup import setup_logging

# Page configuration
st.set_page_config(
    page_title="Neural Research Assistant",
    page_icon="🧠",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for futuristic design
st.markdown("""
<style>
    /* Futuristic gradient background */
    .stApp {
        background: linear-gradient(135deg, #0a0e27 0%, #1a1a2e 50%, #16213e 100%);
    }

    /* Glowing headers */
    h1 {
        background: linear-gradient(90deg, #00d4ff, #7b2ff7);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        font-weight: 800;
        text-shadow: 0 0 20px rgba(0, 212, 255, 0.3);
    }

    /* Card-like containers with glow */
    .stMarkdown, .stTextInput, .stButton {
        backdrop-filter: blur(10px);
    }

    /* Neon accent lines */
    hr {
        border: none;
        height: 2px;
        background: linear-gradient(90deg, transparent, #00d4ff, transparent);
        box-shadow: 0 0 10px #00d4ff;
    }

    /* Futuristic input fields */
    .stTextInput input {
        background: rgba(255, 255, 255, 0.05);
        border: 1px solid rgba(0, 212, 255, 0.3);
        border-radius: 8px;
        color: #ffffff;
        transition: all 0.3s;
    }

    .stTextInput input:focus {
        border-color: #00d4ff;
        box-shadow: 0 0 15px rgba(0, 212, 255, 0.5);
    }

    /* Glowing buttons */
    .stButton button {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        border: none;
        border-radius: 8px;
        color: white;
        font-weight: 600;
        transition: all 0.3s;
        box-shadow: 0 4px 15px rgba(102, 126, 234, 0.4);
    }

    .stButton button:hover {
        box-shadow: 0 6px 25px rgba(102, 126, 234, 0.6);
        transform: translateY(-2px);
    }

    /* Sidebar styling */
    [data-testid="stSidebar"] {
        background: linear-gradient(180deg, rgba(10, 14, 39, 0.95), rgba(22, 33, 62, 0.95));
        border-right: 1px solid rgba(0, 212, 255, 0.2);
    }

    /* Success/Info boxes */
    .stSuccess, .stInfo, .stWarning {
        border-radius: 8px;
        border-left: 4px solid #00d4ff;
        backdrop-filter: blur(10px);
    }

    /* Tab styling */
    .stTabs [data-baseweb="tab-list"] {
        gap: 8px;
    }

    .stTabs [data-baseweb="tab"] {
        background: rgba(255, 255, 255, 0.05);
        border-radius: 8px;
        padding: 8px 16px;
        transition: all 0.3s;
    }

    .stTabs [aria-selected="true"] {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        box-shadow: 0 4px 15px rgba(102, 126, 234, 0.4);
    }

    /* Progress bar */
    .stProgress > div > div {
        background: linear-gradient(90deg, #00d4ff, #7b2ff7);
    }
</style>
""", unsafe_allow_html=True)


def initialize_app():
    """Initialize application with config and logging."""
    try:
        config = load_config()
        logger = setup_logging(
            log_file=config['logging']['file'],
            level=config['logging']['level'],
            console=config['logging'].get('console', True)
        )
        return config, logger
    except Exception as e:
        st.error(f"Configuration error: {e}")
        st.info(
            "Make sure you have:\n"
            "1. Copied config.yaml.template to config.yaml\n"
            "2. Set your ANTHROPIC_API_KEY environment variable"
        )
        st.stop()


def main():
    """Main Streamlit application."""

    # Header
    st.title("🧠 Neural Research Assistant")
    st.markdown(
        "**AI-Powered Deep Research** • Ask any question and watch as Claude analyzes the web, "
        "extracts key insights, and synthesizes comprehensive findings."
    )

    # Initialize
    if 'config' not in st.session_state:
        st.session_state.config, st.session_state.logger = initialize_app()

    config = st.session_state.config

    # Sidebar settings
    with st.sidebar:
        st.header("⚙️ Settings")

        max_results = st.slider(
            "Sources per query",
            min_value=3,
            max_value=10,
            value=config['search'].get('max_results_per_query', 5),
            help="Number of search results to fetch per sub-query"
        )

        # Update config with user preference
        config['search']['max_results_per_query'] = max_results

        st.divider()

        st.header("ℹ️ About")
        st.markdown(
            """
            **Powered by AI:**
            - 🤖 **Claude Sonnet 4.5** - Reasoning & synthesis
            - 🔍 **Google Custom Search** - Web discovery
            - 📄 **Trafilatura** - Content extraction

            **Research Pipeline:**
            1. 🧠 Decomposes question into sub-queries
            2. 🌐 Searches and fetches web sources
            3. 📊 Extracts key facts with confidence levels
            4. 🔬 Synthesizes findings & identifies gaps
            """
        )

    # Main input area
    if 'current_question' not in st.session_state:
        st.session_state.current_question = ""

    question = st.text_input(
        "Research Question",
        value=st.session_state.current_question,
        placeholder="e.g., What are the latest advances in multi-agent AI systems?",
        help="Ask any research question. The more specific, the better the results."
    )

    # Update session state when text changes
    if question != st.session_state.current_question:
        st.session_state.current_question = question

    # Example questions as clickable chips
    st.markdown("**💡 Quick Start:**")
    examples = [
        "What are the benefits of microservices architecture?",
        "How does CRISPR gene editing work?",
        "What are the latest developments in quantum computing?",
        "What is the current state of fusion energy research?",
        "How do transformer models work in natural language processing?"
    ]

    cols = st.columns(2)
    for idx, ex in enumerate(examples):
        with cols[idx % 2]:
            if st.button(f"🔹 {ex}", key=f"example_{idx}", use_container_width=True):
                st.session_state.current_question = ex
                st.session_state.trigger_research = True
                st.rerun()

    st.divider()

    # Research button or auto-trigger
    start_research = False
    if 'trigger_research' in st.session_state and st.session_state.trigger_research:
        start_research = True
        st.session_state.trigger_research = False
        question = st.session_state.current_question
    elif st.button("🔬 Start Research", type="primary", disabled=not question):
        start_research = True

    if start_research:
        if not question:
            st.error("Please enter a research question")
            return

        # Progress tracking
        progress_bar = st.progress(0)
        status_text = st.empty()

        try:
            # Initialize orchestrator
            orchestrator = ResearchOrchestrator(config)

            # Step 1: Decompose
            status_text.text("🧠 Neural query decomposition...")
            progress_bar.progress(15)

            # Step 2: Search
            status_text.text("🌐 Scanning web via Google Custom Search...")
            progress_bar.progress(30)

            # We can't track individual steps since research() is one call
            # but we show progress to indicate activity
            status_text.text("📡 Fetching and parsing content...")
            progress_bar.progress(45)

            status_text.text("🔍 AI fact extraction in progress...")
            progress_bar.progress(65)

            status_text.text("⚡ Claude synthesizing insights...")
            progress_bar.progress(80)

            # Run research (this does all the work)
            report = orchestrator.research(question)

            progress_bar.progress(100)
            status_text.text("✨ Analysis complete! Results ready.")

            # Store report in session state
            st.session_state.report = report

        except ValueError as e:
            st.error(f"Research failed: {e}")
            return
        except Exception as e:
            st.error(f"Unexpected error: {e}")
            st.exception(e)
            return

    # Display results if available
    if 'report' in st.session_state:
        report = st.session_state.report

        st.divider()

        # Create tabs for different views
        tab1, tab2, tab3, tab4 = st.tabs(
            ["📊 Summary", "🔍 Detailed Findings", "📚 Sources", "📄 Full Report"]
        )

        with tab1:
            st.markdown("## Summary")
            st.markdown(report.synthesis.answer)

            st.markdown("---")

            col1, col2 = st.columns(2)

            with col1:
                st.markdown("### ✅ Areas of Agreement")
                if report.synthesis.agreements:
                    for agreement in report.synthesis.agreements:
                        st.success(agreement)
                else:
                    st.info("No clear agreements identified")

                if report.synthesis.contradictions:
                    st.markdown("### ⚠️ Contradictions")
                    for contradiction in report.synthesis.contradictions:
                        with st.expander(f"⚠️ {contradiction.issue}"):
                            st.markdown(f"**Sources:** {', '.join(contradiction.sources)}")
                            st.markdown(f"**Explanation:** {contradiction.explanation}")

            with col2:
                st.markdown("### ❓ Knowledge Gaps")
                if report.synthesis.gaps:
                    for gap in report.synthesis.gaps:
                        st.warning(gap)
                else:
                    st.info("No significant gaps identified")

        with tab2:
            st.markdown("## Key Findings")

            st.markdown(f"*Extracted {len(report.facts)} facts from {len(report.sources)} sources*")

            # Group by confidence
            high_conf = [f for f in report.facts if f.confidence == 'high']
            med_conf = [f for f in report.facts if f.confidence == 'medium']
            low_conf = [f for f in report.facts if f.confidence == 'low']

            if high_conf:
                st.markdown("### ✓ High Confidence")
                for fact in high_conf:
                    st.markdown(f"**{fact.claim}**")
                    if fact.caveat:
                        st.caption(f"Caveat: {fact.caveat}")
                    st.caption(f"[Source]({fact.source_url})")
                    st.markdown("")

            if med_conf:
                st.markdown("### ○ Medium Confidence")
                for fact in med_conf:
                    st.markdown(f"**{fact.claim}**")
                    if fact.caveat:
                        st.caption(f"Caveat: {fact.caveat}")
                    st.caption(f"[Source]({fact.source_url})")
                    st.markdown("")

            if low_conf:
                st.markdown("### ? Low Confidence")
                for fact in low_conf:
                    st.markdown(f"**{fact.claim}**")
                    if fact.caveat:
                        st.caption(f"Caveat: {fact.caveat}")
                    st.caption(f"[Source]({fact.source_url})")
                    st.markdown("")

        with tab3:
            st.markdown("## Sources")

            for idx, source in enumerate(report.sources, 1):
                with st.expander(f"{idx}. {source.title}"):
                    st.markdown(f"**URL:** [{source.url}]({source.url})")
                    st.markdown(f"**Accessed:** {source.fetch_time.strftime('%Y-%m-%d %H:%M:%S')}")
                    st.markdown(f"**Content length:** {len(source.content)} characters")

        with tab4:
            st.markdown("## Full Markdown Report")

            # Generate markdown
            markdown_report = report.to_markdown()

            # Display in text area
            st.text_area(
                "Report Content",
                markdown_report,
                height=400,
                help="Copy this text or download using the button below"
            )

            # Download button
            st.download_button(
                label="📥 Download Report as Markdown",
                data=markdown_report,
                file_name=f"research_report_{report.timestamp.strftime('%Y%m%d_%H%M%S')}.md",
                mime="text/markdown"
            )

        # Clear results button
        if st.button("🗑️ Clear Results"):
            del st.session_state.report
            st.rerun()


if __name__ == "__main__":
    main()
