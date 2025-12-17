# 🔍 Agentic Research Assistant

An autonomous Python application that takes a research question and produces a structured report with citations by searching the web, extracting key facts, and synthesizing findings using Claude AI.

## Features

- **Autonomous Research**: Agent breaks complex questions into sub-queries automatically
- **Web Search**: Uses DuckDuckGo (no API key needed)
- **Smart Extraction**: Claude identifies key facts and assesses confidence
- **Synthesis**: Compares sources, identifies agreements, contradictions, and knowledge gaps
- **Clean Interface**: Streamlit web UI with progress tracking
- **Detailed Reports**: Markdown reports with citations and methodology

## Architecture

```
User Question
    ↓
Query Decomposer (Claude: break into 3-5 sub-queries)
    ↓
Search Engine (DuckDuckGo: find sources)
    ↓
Content Fetcher (Trafilatura: extract clean text)
    ↓
Fact Extractor (Claude: extract key facts)
    ↓
Synthesizer (Claude: compare sources, find patterns)
    ↓
Markdown Report (with citations)
```

### Key Agent Decision Points

1. **Query Decomposition**: How to break down complex questions for optimal coverage
2. **Fact Extraction**: What information is relevant and how reliable is it
3. **Synthesis**: How to reconcile conflicting information and identify gaps

## Quick Start

### Prerequisites

- Python 3.11+
- Anthropic API key

### Installation

1. Clone the repository:
```bash
git clone https://github.com/EiriniOr/research-assistant.git
cd research-assistant
```

2. Install dependencies using Poetry:
```bash
poetry install
```

Or using pip:
```bash
pip install -r requirements.txt
```

3. Configure API key:

Copy the config template:
```bash
cp config.yaml.template config.yaml
```

Set your API key (choose one method):

**Option A: Environment variable (recommended)**
```bash
export ANTHROPIC_API_KEY='your-key-here'
```

**Option B: Edit config.yaml**
```yaml
anthropic:
  api_key: "sk-ant-your-key-here"
```

### Running the Application

Start the Streamlit interface:
```bash
poetry run streamlit run src/main.py
```

Or with pip:
```bash
streamlit run src/main.py
```

The app will open in your browser at `http://localhost:8501`

## Usage

1. Enter a research question in the text input
2. Click "Start Research"
3. Watch the agent work through the steps:
   - Breaking down the question
   - Searching for sources
   - Fetching content
   - Extracting facts
   - Synthesizing findings
4. View results in tabs:
   - **Summary**: Key answer with agreements and gaps
   - **Detailed Findings**: All extracted facts by confidence level
   - **Sources**: List of consulted sources
   - **Full Report**: Markdown report ready for download

### Example Questions

- "What are the benefits of microservices architecture?"
- "How does CRISPR gene editing work?"
- "What are the latest developments in quantum computing?"
- "What is the current state of fusion energy research?"
- "How do transformer models work in natural language processing?"

## Project Structure

```
research-assistant/
├── src/
│   ├── main.py                 # Streamlit UI
│   ├── agent/
│   │   ├── orchestrator.py     # Main workflow coordinator
│   │   └── prompts.py          # Claude prompts
│   ├── search/
│   │   ├── search_engine.py    # DuckDuckGo wrapper
│   │   ├── content_fetcher.py  # HTML extraction
│   │   └── search_types.py     # Data models
│   ├── analysis/
│   │   ├── query_decomposer.py # Question breakdown
│   │   ├── fact_extractor.py   # Fact extraction
│   │   └── synthesizer.py      # Synthesis logic
│   └── utils/
│       ├── config_loader.py    # Config management
│       └── logging_setup.py    # Logging setup
├── data/
│   └── reports/                # Generated reports
├── logs/                       # Application logs
├── config.yaml.template        # Config template
└── README.md
```

## Configuration

Edit `config.yaml` to customize:

```yaml
# Claude settings
anthropic:
  model: "claude-sonnet-4-5-20250929"
  temperature: 0.3  # Lower = more focused

# Search settings
search:
  max_results_per_query: 5  # Sources per sub-query

# Agent behavior
agent:
  max_subqueries: 5
  min_subqueries: 3
  facts_per_source: 5

# Logging
logging:
  level: "INFO"  # DEBUG for more detail
```

## Error Handling

The agent is designed to be resilient:

- **Search failures**: Retries with exponential backoff, continues with partial results
- **Content fetch errors**: Logs warnings, skips problematic sources
- **Claude API rate limits**: Automatic retry with backoff
- **Decomposition failures**: Falls back to original question
- **No sources found**: Clear error message with suggestions

## Development

### Running Tests

```bash
poetry run pytest
```

### Code Formatting

```bash
poetry run black src/
poetry run ruff check src/
```

### Logging

Logs are written to `logs/research.log`. Set log level in `config.yaml`:

```yaml
logging:
  level: "DEBUG"  # For detailed debugging
```

## Future Enhancements

- [ ] Add Tavily API as alternative search engine
- [ ] Support PDF sources
- [ ] Add caching for search results
- [ ] Multi-language support
- [ ] Export to PDF/HTML
- [ ] Save and compare research history
- [ ] Source diversity scoring

## Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b eirini/feature-name`)
3. Commit your changes
4. Push to your fork
5. Open a Pull Request

## License

MIT License

## Acknowledgments

- **Claude AI** by Anthropic for reasoning and synthesis
- **DuckDuckGo** for privacy-focused web search
- **Trafilatura** for robust content extraction
- **Streamlit** for the web interface

---

**Built as a portfolio project demonstrating:**
- Agentic AI workflows
- Claude API integration
- Web scraping and content extraction
- Clean, modular Python architecture
- Error handling and graceful degradation
