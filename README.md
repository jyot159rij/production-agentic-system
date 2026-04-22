# Production Agentic System

A production-grade AI agent that orchestrates 5 tools to answer multi-step queries reliably.

Built for the LEC AI Engineer assignment.

## What it does

- Accepts a natural language query via REST API
- Generates an explicit plan before executing any tools
- Calls tools in parallel where independent (asyncio)
- Reflects after each round to decide if done
- Returns final answer with full tool trace and cost breakdown
- Hard budget cap — rejects when token cost exceeds limit

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
| Avg latency | 21.57s per query |
| Total eval cost | $0.088 for all 10 queries |

## Project Structure

```
production-agentic-system/
├── agent/
│   ├── loop.py          # Core agent loop
│   ├── planner.py       # Planning step
│   ├── reflector.py     # Reflection + termination
│   ├── budget.py        # Token + cost tracking
│   └── state.py         # AgentState dataclass
├── tools/
│   ├── calculator.py
│   ├── weather.py
│   ├── web_search.py
│   ├── knowledge_base.py
│   └── document_qa.py
├── eval/
│   ├── queries.json     # 10 test queries
│   ├── run_eval.py      # Evaluation runner
│   └── run_ablation.py  # Prompt ablation test
├── tests/
│   ├── test_tools.py
│   ├── test_budget.py
│   └── test_agent_loop.py
├── docs/                # Sample documents for QA tool
├── main.py              # FastAPI app
├── setup_kb.py          # Knowledge base setup
├── conftest.py          # Pytest config
├── REPORT.md            # Written report
├── ARCHITECTURE.md      # Architecture decisions
├── NEXT_STEPS.md        # Roadmap
└── AI_USAGE.md          # AI usage note
```

## Setup

### Requirements
- Python 3.12+
- Anthropic API key — https://console.anthropic.com
- Tavily API key — https://tavily.com (free tier)

### Install

```bash
git clone https://github.com/jyot159rij/production-agentic-system.git
cd production-agentic-system
python -m venv venv
venv\Scripts\activate
pip install -r requirements.txt
```

### Configure

Create a `.env` file in the project root:

```
ANTHROPIC_API_KEY=your_key_here
TAVILY_API_KEY=your_key_here
```

### Set up knowledge base

```bash
python setup_kb.py
```

### Run the API

```bash
uvicorn main:app --reload
```

API live at: `http://127.0.0.1:8000`

Interactive docs at: `http://127.0.0.1:8000/docs`

### Run tests

```bash
pytest tests/ -v
```

### Run evaluation

```bash
python -m eval.run_eval
```

## API Usage

### POST /query

Request:
```json
{
  "query": "What is the weather in London and convert to Fahrenheit?",
  "max_budget_usd": 0.10
}
```

Response:
```json
{
  "query": "What is the weather in London and convert to Fahrenheit?",
  "plan": "PLAN:\n1. weather - get London temperature\n2. calculator - convert Celsius to Fahrenheit",
  "final_answer": "London is currently 14°C which is 57.2°F...",
  "tool_calls": [
    {"tool": "weather", "input": {"input": "London"}, "observation": "London: 14°C", "success": true},
    {"tool": "calculator", "input": {"expression": "14 * 9/5 + 32"}, "observation": "Result: 57.2", "success": true}
  ],
  "iterations": 1,
  "budget": {
    "input_tokens": 950,
    "output_tokens": 210,
    "total_tokens": 1160,
    "cost_usd": 0.002
  },
  "is_done": true
}
```

### GET /tools
Returns all available tools with descriptions.

### GET /health
Health check.

## Architecture

```
POST /query
     ↓
[Planner LLM] — generates step-by-step plan
     ↓
[Tool Executor] — asyncio.gather for parallel execution
     ↓
[Reflector LLM] — done or needs more tools?
     ↓
[Answer LLM] — synthesises observations into final answer
     ↓
Response with tool trace + budget breakdown
```

## Known Limitations

- Agent over-calls web_search as a fallback even when query is already answered — documented honestly in REPORT.md
- Average latency of 21s is too slow for real-time use
- No persistent memory across queries
- Single user only — no concurrency handling at scale