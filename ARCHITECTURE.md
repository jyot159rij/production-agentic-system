# Architecture Decisions

## Stack Overview

```
FastAPI (API layer)
    ↓
Agent Loop (agent/loop.py)
    ├── Planner (Claude Haiku 4.5)
    ├── Tool Executor (asyncio.gather for parallel)
    ├── Reflector (Claude Haiku 4.5)
    └── Answer Generator (Claude Haiku 4.5)
         ↓
Tools
    ├── Calculator (simpleeval)
    ├── Weather (wttr.in)
    ├── Web Search (Tavily)
    ├── Knowledge Base (SQLite)
    └── Document QA (ChromaDB + sentence-transformers)
```

## Key Decisions

### Claude Haiku 4.5 over GPT-4o
Haiku 4.5 costs $1/$5 per million tokens vs GPT-4o at $2.50/$10. For an agent that 
makes 3+ LLM calls per query, this difference compounds fast. Haiku is fast enough 
for planning and reflection tasks. Would use Sonnet for the final answer step in 
production where quality matters more.

### Custom agent loop over LangChain
LangChain AgentExecutor hides the reflection logic inside abstractions. For a 
production system where you need to control exactly when to terminate, retry, and 
track costs, a custom loop gives full visibility. The tradeoff is more code to 
maintain.

### ChromaDB over Pinecone/Weaviate
ChromaDB runs locally with zero setup — no Docker, no account, no network dependency. 
For a local assignment this is the right call. In production I would switch to Qdrant 
(self-hosted) or Pinecone (managed) for horizontal scaling and persistence guarantees.

### SQLite for knowledge base
A real knowledge base would be PostgreSQL with full-text search. SQLite with LIKE 
queries is enough for a 10-row demo and keeps the setup to one file. Tradeoff: no 
fuzzy matching, case-sensitive quirks on some platforms.

### Tavily over SerpAPI/Google Search
Tavily is purpose-built for LLM agents — returns clean text summaries rather than 
raw HTML. Free tier (1000 searches/month) is sufficient for development. SerpAPI 
returns richer structured data but requires more parsing code.

### simpleeval over raw eval()
Raw Python eval() executes arbitrary code — a security hole if the LLM hallucinates 
a malicious expression. simpleeval only allows mathematical operations. No tradeoff 
here — raw eval() should never be used in agent tools.

## Rejected Alternatives

| Option | Rejected because |
|---|---|
| LangGraph | Adds complexity without control benefit for this scope |
| Pinecone | Cloud-only, requires account, overkill for local demo |
| OpenAI embeddings | Costs money per call, sentence-transformers is free and sufficient |
| Flask | No native async support, slower to write |
| Redis for budget state | Overkill — in-memory BudgetTracker is sufficient for single-user |

## What Would Break at 100 Concurrent Users

1. BudgetTracker is instantiated per request — fine
2. ChromaDB has no connection pooling — concurrent writes would corrupt the index
3. SQLite has file-level locking — concurrent reads fine, concurrent writes would queue
4. Tavily free tier has rate limits — would hit them immediately at 100 users
5. No request queuing — FastAPI would accept all 100 and they'd compete for LLM API rate limits