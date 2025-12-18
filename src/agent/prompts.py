"""Claude prompt templates for the research assistant agent."""

# Query Decomposition Prompt
# AGENT DECISION POINT: How to break down a complex question into searchable sub-queries
DECOMPOSE_PROMPT = """You are a research assistant helping decompose complex questions into searchable sub-queries.

Original question: {question}

Your task is to break this into 2-3 specific, searchable sub-queries that:
1. Cover key aspects of the main question
2. Can be answered by web search
3. Are specific enough for good search results

AGENT REASONING: Consider what information is needed to fully answer this question. Think about:
- Core concepts that need definition
- Related technologies or methods to explore
- Different perspectives or use cases
- Recent developments or current state
- Practical implications or applications

Return ONLY a JSON array of query strings, nothing else:
["query 1", "query 2", "query 3"]

Example:
Question: "What are the benefits of microservices architecture?"
Output: ["microservices architecture definition benefits", "microservices vs monolithic architecture comparison", "microservices implementation challenges", "successful microservices case studies"]
"""

# Fact Extraction Prompt
# AGENT DECISION POINT: What facts are relevant and how to assess their reliability
EXTRACT_PROMPT = """You are extracting key facts from a source for research purposes.

Research question: {question}

Source URL: {url}
Source content:
{content}

Your task is to extract 2-3 key facts or claims that are relevant to answering the research question.

For each fact:
1. State it clearly and concisely
2. Note any caveats or conditions
3. Rate confidence (high/medium/low) based on:
   - Whether the source provides evidence
   - Whether it's a primary or secondary source
   - Whether it's opinion vs fact

AGENT REASONING: Focus on factual claims, not opinions. Note contradictions with common knowledge. Prioritize information that directly answers the research question.

Return ONLY valid JSON in this format:
{{
  "facts": [
    {{
      "claim": "Clear, factual statement",
      "caveat": "Any limitations or conditions (or null)",
      "confidence": "high"
    }}
  ]
}}

If no relevant facts found, return: {{"facts": []}}
"""

# Synthesis Prompt
# AGENT DECISION POINT: How to reconcile conflicting information and identify gaps
SYNTHESIZE_PROMPT = """You are synthesizing research findings from multiple sources.

Original question: {question}

Facts gathered from {num_sources} sources:
{facts_json}

Your task is to analyze these facts and provide:

1. AREAS OF AGREEMENT: What do multiple sources agree on? List the key consensus points.

2. CONTRADICTIONS: Where do sources conflict? For each contradiction:
   - What is the conflicting claim?
   - Which sources support each side?
   - Why might this conflict exist? (different contexts, outdated info, etc.)

3. KNOWLEDGE GAPS: What important aspects are missing or unclear? What questions remain unanswered?

4. OVERALL ANSWER: Provide a concise answer (1-2 paragraphs max). Focus on key findings only. Weigh evidence quality - higher confidence facts should carry more weight.

AGENT REASONING:
- Look for patterns across sources
- Higher confidence facts should be weighted more heavily
- Identify potential biases or limitations in sources
- Be honest about what we don't know

Return ONLY valid JSON in this format:
{{
  "agreements": [
    "Point of agreement 1",
    "Point of agreement 2"
  ],
  "contradictions": [
    {{
      "issue": "Description of the contradiction",
      "sources": ["url1", "url2"],
      "explanation": "Why this might exist"
    }}
  ],
  "gaps": [
    "Missing information 1",
    "Unanswered question 2"
  ],
  "answer": "Concise answer to the original question. 1-2 paragraphs maximum. Focus on key findings only."
}}

If there are no contradictions or gaps, use empty arrays: "contradictions": [], "gaps": []
"""
