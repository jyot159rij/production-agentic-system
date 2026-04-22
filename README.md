# production-agentic-system
Production-grade agentic system with 5 tools - LEC AI assignment
# Production Agentic System

A production-grade AI agent that orchestrates 5 tools to answer multi-step queries reliably.

Built for the LEC AI Engineer assignment.

## What it does

- Accepts a natural language query via REST API
- Generates an explicit plan before executing
- Calls tools in parallel where independent
- Reflects after each round to decide if done
- Returns final answer with full tool trace and cost breakdown

## Tools

| Tool | Purpose |
|---|---|
| `calculator` | Safe mathematical expression evaluation |
| `weather` | Current weather for any city |
| `web_search` | Live web search via Tavily |
| `knowledge_base` | Internal company facts via SQLite |
| `document_qa` | Semantic search over internal documents |

## Evaluation Results

| Metric | Result |
|---|---|
| Success rate | 10/10 (100%) |
| Easy queries | 3/3 |
| Medium queries | 4/4 |
| Hard queries | 3/3 |
| Avg latency | 27s per query |
| Total eval cost | $0.116 |

## Setup

### Requirements
- Python 3.12+
- Anthropic API key
- Tavily API key (free tier)

### Install

```bash
git clone https://github.com/jyot159rij/production-agentic-system.git
cd production-agentic-system
python -m venv venv
venv\Scripts\activate        # Windows
pip install -r requirements.txt
```

### Configure

Create a `.env` file in the project root:

ANTHROPIC_API_KEY=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
TAVILY_API_KEY=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

### Set up knowledge base

```bash
python setup_kb.py
```

### Run

```bash
uvicorn main:app --reload
```

API is live at `http://127.0.0.1:8000`

Interactive docs at `http://127.0.0.1:8000/docs`

### Run tests

```bash
pytest tests/ -v
```

### Run evaluation

```bash
python -m eval.run_eval
```

## API

### POST /query

```json
{
  "query": "What is the weather in London and convert to Fahrenheit?",
  "max_budget_usd": 0.10
}
```

Response:

```json
{
  "query": "...",
  "plan": "PLAN:\n1. weather - get London weather\n2. calculator - convert to F",
  "final_answer": "London is currently 14°C (57.2°F)...",
  "tool_calls": [...],
  "iterations": 2,
  "budget": {"input_tokens": 900, "output_tokens": 200, "cost_usd": 0.0012},
  "is_done": true
}
```

### GET /tools

Returns list of all available tools with descriptions.

### GET /health

Health check endpoint.

## Architecture
POST /query
↓
[Planner] — generates step-by-step plan
↓
[Tool Executor] — runs tools (parallel where independent)
↓
[Reflector] — decides: done or needs more tools
↓
[Final Answer] — synthesises observations into answer

## Known limitations

- Agent over-calls web_search as a fallback even when query is already answered
- Average latency of 27s is too slow for real-time use
- No persistent memory across queries
- Single-user only — no concurrency handling