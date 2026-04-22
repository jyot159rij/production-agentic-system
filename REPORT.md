# Written Report — Production Agentic System

## What I Built

A multi-tool AI agent exposed via a FastAPI REST API. The agent takes a natural language 
query, generates an explicit plan, executes tools (sequentially or in parallel), reflects 
on observations, and produces a final answer with full cost tracking.

The system uses Claude Haiku 4.5 as the LLM backbone across three roles: planner, 
reflector, and answer generator. Five tools are wired up: a calculator, weather API, 
web search, SQLite knowledge base, and a semantic document QA system backed by ChromaDB.

## Evaluation Results

Ran 10 multi-step queries graded on tool usage and answer correctness.

- Success rate: 10/10 (100%)
- Easy: 3/3 | Medium: 4/4 | Hard: 3/3
- Average latency: 27.1s per query
- Total eval cost: $0.116 across all 10 queries (~$0.012 per query)

Prompt ablation across 5 queries: both detailed (V1) and minimal (V2) prompts scored 
5/5. This suggests the agent's success is driven more by the tool execution and 
reflection logic than by prompt verbosity.

## What Broke

**1. Web search over-calling**
The agent repeatedly calls web_search as a fallback even after the query has already 
been answered by a more specific tool. Query 1 (simple multiplication) correctly used 
the calculator but then fired web_search 10 additional times before terminating. 
Root cause: the reflector prompt does not strongly penalise redundant tool calls, and 
the initial parallel execution fires tools based on keyword matching rather than intent.

**2. Latency**
At 27s average, the system is too slow for real-time use. Each query makes 3 LLM calls 
minimum (planner + reflector + answer) plus tool API calls. The reflector loop runs 
multiple times even when one iteration would suffice.

**3. Prompt ablation showed no difference**
V1 (detailed, step-by-step instructions) and V2 (minimal, 3-line prompt) both scored 
100% on the ablation set. This is honest — for simple queries, prompt detail does not 
drive success. I expect the gap would appear on more ambiguous or multi-constraint 
queries where planning order matters.

## What I Learned

Building the reflection loop was harder than expected. The naive approach — "keep 
calling tools until the reflector says done" — produces runaway behaviour where the 
agent calls web_search indefinitely as a catch-all. A hard iteration cap (MAX_ITERATIONS) 
is essential, not optional.

Token tracking is easy to add but easy to get wrong on pricing. The budget.py class 
was initially using incorrect per-token rates — caught this during testing.

The evaluation framework revealed more than manual testing. Running 10 structured 
queries showed the web_search over-calling pattern immediately, which I would not have 
spotted from spot-checking alone.