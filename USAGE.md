# Usage Guide

## First Time Setup

1. **Set your API key** (required for Claude):
   ```bash
   export ANTHROPIC_API_KEY='sk-ant-your-key-here'
   ```

   Add to `.bashrc` or `.zshrc` to persist:
   ```bash
   echo 'export ANTHROPIC_API_KEY="your-key"' >> ~/.zshrc
   source ~/.zshrc
   ```

2. **Run the app**:
   ```bash
   poetry run streamlit run src/main.py
   ```

3. Open browser to `http://localhost:8501`

## Using the App

### Basic Workflow

1. **Enter Question**: Type your research question
2. **Adjust Settings** (optional): Use sidebar to change sources per query
3. **Click "Start Research"**: Watch the agent work through steps
4. **Review Results**: View in multiple tabs
5. **Download Report**: Get markdown file

### Tips for Good Questions

**✅ Good Questions:**
- Specific and focused: "What are the benefits of microservices?"
- Technical topics: "How do transformers work in NLP?"
- Recent developments: "Latest advances in quantum computing"

**❌ Avoid:**
- Too broad: "Tell me about technology"
- Subjective: "What's the best programming language?"
- Opinion-based: "Should I use React or Vue?"

### Understanding Results

**Summary Tab:**
- Main answer synthesized from all sources
- Areas of agreement across sources
- Identified contradictions with explanations
- Knowledge gaps in the research

**Detailed Findings Tab:**
- All extracted facts organized by confidence:
  - ✓ High: Well-supported by evidence
  - ○ Medium: Some support or caveats
  - ? Low: Unclear or limited evidence

**Sources Tab:**
- All consulted sources with URLs
- Access timestamps
- Content length

**Full Report Tab:**
- Complete markdown report
- Download button for saving

### Example Session

```
Question: "How does CRISPR gene editing work?"

Agent Steps:
1. Breaks into sub-queries:
   - "CRISPR gene editing mechanism"
   - "Cas9 protein function in CRISPR"
   - "CRISPR applications and uses"

2. Searches DuckDuckGo for each query (5 sources each)

3. Fetches and cleans content from ~15 URLs

4. Extracts ~50 key facts with confidence levels

5. Synthesizes findings:
   - Agreement: CRISPR uses Cas9 to cut DNA
   - Agreement: Targets specific sequences via guide RNA
   - Gap: Long-term effects still being studied

6. Generates report with citations
```

## Troubleshooting

### "Config file not found"
- Copy `config.yaml.template` to `config.yaml`
- Ensure you're in the project directory

### "ANTHROPIC_API_KEY not set"
- Export the key: `export ANTHROPIC_API_KEY='your-key'`
- Check it's set: `echo $ANTHROPIC_API_KEY`

### "No sources found"
- Check internet connection
- Try a more specific question
- Check logs in `logs/research.log`

### Rate Limit Errors
- Agent automatically retries with backoff
- If persistent, wait a few minutes
- Consider reducing sources per query

### Poor Quality Results
- Try more specific questions
- Increase sources per query in sidebar
- Check if topic is too recent/niche
- Review logs for fetch failures

## Advanced Usage

### Debugging

Enable debug logging in `config.yaml`:
```yaml
logging:
  level: "DEBUG"
```

Check logs:
```bash
tail -f logs/research.log
```

### Customizing Agent Behavior

Edit `config.yaml`:

```yaml
agent:
  max_subqueries: 5      # More = broader coverage
  min_subqueries: 3      # Fewer = faster
  facts_per_source: 5    # More = more detailed

search:
  max_results_per_query: 5  # More = more sources, slower
```

### Command Line Usage

For programmatic use, import directly:

```python
from src.agent.orchestrator import ResearchOrchestrator
from src.utils.config_loader import load_config

config = load_config()
orchestrator = ResearchOrchestrator(config)

report = orchestrator.research("Your question here")
print(report.to_markdown())
```

### Saving Reports

Reports auto-save to `data/reports/` with timestamps.

Enable intermediate data saving in `config.yaml`:
```yaml
output:
  save_intermediate: true  # Saves raw sources for debugging
```

## Best Practices

1. **Start specific**: Narrow questions get better results
2. **Check sources**: Review URLs in Sources tab
3. **Note confidence**: Pay attention to High/Medium/Low markers
4. **Read caveats**: Many facts have important qualifiers
5. **Check gaps**: What the agent couldn't find is often revealing

## Next Steps

- Try the example questions
- Experiment with different topics
- Adjust settings to see impact on results
- Review generated reports in `data/reports/`
- Check logs to understand agent decisions
