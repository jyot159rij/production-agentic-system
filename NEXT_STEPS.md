# What I'd Ship Next — One More Week

## 1. Fix the web_search over-calling (2 days)
The biggest quality issue. The reflector needs a smarter termination signal — 
specifically, tracking which tools have already been called and blocking redundant 
calls. Would add a `seen_tools` set to AgentState and pass it to the reflector prompt. 
Expected impact: latency drops from 27s to under 10s, cost drops by 60%.

## 2. Streaming responses (1 day)
Currently the API waits for the full agent run before returning. For a 27s query 
this is a terrible user experience. FastAPI supports Server-Sent Events — stream 
each tool observation as it arrives so the user sees progress in real time. 
This is table-stakes for any production agent UI.

## 3. Conversation memory (1 day)
Right now every query is stateless. A real agent needs to remember context across 
turns — "what was the weather you told me earlier?" should work. Would add a Redis 
session store keyed by session_id, passed in the request header.

## 4. Concurrency and rate limit handling (1 day)
Add a request queue with a worker pool (asyncio.Semaphore limiting to 10 concurrent 
agent runs). Add exponential backoff on Tavily and Anthropic API calls. Without this 
the system falls over at more than 5 concurrent users.

## 5. Observability (half day)
Add structured logging (structlog) with trace_id per request, tool call durations, 
and cost per request. Feed into a simple dashboard. Right now failures are invisible 
in production — you only know something broke when a user complains.