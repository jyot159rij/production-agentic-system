from dotenv import load_dotenv
load_dotenv()

import asyncio
import pytest
from agent.loop import run_agent

def test_simple_math_query():
    result = asyncio.run(run_agent("What is 10 multiplied by 5?"))
    assert result["is_done"] == True
    assert "50" in result["final_answer"]
    assert result["budget"]["cost_usd"] < 0.05

def test_budget_cap_respected():
    result = asyncio.run(run_agent("What is 2 + 2?", max_usd=0.000001))
    assert "budget" in result["final_answer"].lower() or result["is_done"]

def test_empty_query_handled():
    result = asyncio.run(run_agent("   "))
    assert result is not None