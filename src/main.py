"""Streamlit web interface for the Research Assistant."""

from datetime import datetime

import streamlit as st

from src.agent.orchestrator import ResearchOrchestrator
from src.utils.config_loader import load_config
from src.utils.logging_setup import setup_logging

# Page configuration
st.set_page_config(
    page_title="Agentic Research Assistant",
    page_icon="🔍",
    layout="wide",
    initial_sidebar_state="expanded"
)


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
    st.title("🔍 Agentic Research Assistant")
    st.markdown(
        "Ask a research question and I'll search, analyze, and synthesize findings from multiple sources."
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
            This tool uses:
            - **Claude** for reasoning & synthesis
            - **DuckDuckGo** for web search
            - **Trafilatura** for content extraction

            The agent:
            1. Breaks your question into sub-queries
            2. Searches and fetches sources
            3. Extracts key facts
            4. Synthesizes findings
            """
        )

    # Main input area
    question = st.text_input(
        "Research Question",
        placeholder="e.g., What are the latest advances in multi-agent AI systems?",
        help="Ask any research question. The more specific, the better the results."
    )

    # Example questions
    with st.expander("💡 Example Questions"):
        examples = [
            "What are the benefits of microservices architecture?",
            "How does CRISPR gene editing work?",
            "What are the latest developments in quantum computing?",
            "What is the current state of fusion energy research?",
            "How do transformer models work in natural language processing?"
        ]
        for ex in examples:
            if st.button(ex, key=ex):
                question = ex
                st.rerun()

    # Research button
    if st.button("🔬 Start Research", type="primary", disabled=not question):
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
            status_text.text("🧠 Breaking down your question...")
            progress_bar.progress(15)

            # Step 2: Search
            status_text.text("🔍 Searching web sources...")
            progress_bar.progress(30)

            # We can't track individual steps since research() is one call
            # but we show progress to indicate activity
            status_text.text("📥 Fetching content...")
            progress_bar.progress(45)

            status_text.text("📝 Extracting key facts...")
            progress_bar.progress(65)

            status_text.text("🔬 Synthesizing findings...")
            progress_bar.progress(80)

            # Run research (this does all the work)
            report = orchestrator.research(question)

            progress_bar.progress(100)
            status_text.text("✅ Research complete!")

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
