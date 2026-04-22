from dotenv import load_dotenv
load_dotenv()

import asyncio
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import Optional
from agent.loop import run_agent

app = FastAPI(
    title="Production Agentic System",
    description="Multi-tool AI agent with planning, parallel execution and budget control",
    version="1.0.0"
)

class QueryRequest(BaseModel):
    query: str
    max_budget_usd: Optional[float] = 0.10

class QueryResponse(BaseModel):
    query: str
    plan: str
    final_answer: str
    tool_calls: list
    iterations: int
    budget: dict
    is_done: bool

@app.get("/")
def root():
    return {"status": "running", "message": "Production Agentic System is live"}

@app.get("/health")
def health():
    return {"status": "healthy"}

@app.post("/query", response_model=QueryResponse)
async def query_agent(request: QueryRequest):
    if not request.query.strip():
        raise HTTPException(status_code=400, detail="Query cannot be empty")

    if request.max_budget_usd > 1.0:
        raise HTTPException(status_code=400, detail="Budget cap is $1.00 maximum")

    result = await run_agent(
        query=request.query,
        max_usd=request.max_budget_usd
    )

    return QueryResponse(**result)

@app.get("/tools")
def list_tools():
    from tools import TOOLS_MAP
    return {
        "tools": [
            {"name": name, "description": tool.description}
            for name, tool in TOOLS_MAP.items()
        ]
    }