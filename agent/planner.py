import os
import anthropic
from dotenv import load_dotenv
from agent.budget import BudgetTracker

load_dotenv()

client = anthropic.Anthropic(api_key=os.getenv("ANTHROPIC_API_KEY"))

PLANNER_PROMPT = """You are a planning agent. Given a user query and a list of available tools, 
produce a clear step-by-step plan to answer the query.

Available tools:
- calculator: evaluate math expressions
- weather: get current weather for a city
- web_search: search the web for current information
- knowledge_base: look up internal company facts
- document_qa: answer questions from internal documents

Rules:
- State the plan BEFORE doing anything
- Identify which tools are needed and in what order
- If two tools are independent, mark them as PARALLEL
- Be concise — max 5 steps

Respond in this exact format:
PLAN:
1. [tool_name or PARALLEL] - reason
2. [tool_name or PARALLEL] - reason
...
"""

def generate_plan(query: str, budget: BudgetTracker) -> str:
    response = client.messages.create(
        model="claude-haiku-4-5",
        max_tokens=300,
        system=PLANNER_PROMPT,
        messages=[{"role": "user", "content": f"Query: {query}"}]
    )
    budget.add(
        response.usage.input_tokens,
        response.usage.output_tokens
    )
    return response.content[0].text