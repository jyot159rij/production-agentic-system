import os
import anthropic
from dotenv import load_dotenv
from agent.state import AgentState
from agent.budget import BudgetTracker

load_dotenv()

client = anthropic.Anthropic(api_key=os.getenv("ANTHROPIC_API_KEY"))

REFLECTOR_PROMPT = """You are a reflection agent. Given a query, a plan, and tool observations so far,
decide if we have enough information to answer the query or if more tool calls are needed.

Respond in this exact format:
STATUS: DONE or CONTINUE
REASON: one sentence why
NEXT_TOOL: (only if STATUS is CONTINUE) tool_name and input
"""

def reflect(state: AgentState, budget: BudgetTracker) -> dict:
    observations_text = "\n".join([
        f"- {tc.tool_name}({tc.tool_input}) => {tc.observation[:200]}"
        for tc in state.tool_calls
    ])

    response = client.messages.create(
        model="claude-haiku-4-5",
        max_tokens=200,
        system=REFLECTOR_PROMPT,
        messages=[{
            "role": "user",
            "content": f"""Query: {state.query}
Plan: {state.plan}
Observations so far:
{observations_text}"""
        }]
    )

    budget.add(
        response.usage.input_tokens,
        response.usage.output_tokens
    )

    text = response.content[0].text
    is_done = "STATUS: DONE" in text

    next_tool = None
    if not is_done and "NEXT_TOOL:" in text:
        next_tool = text.split("NEXT_TOOL:")[-1].strip()

    return {
        "is_done": is_done,
        "reflection_text": text,
        "next_tool": next_tool
    }