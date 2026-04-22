import os
import asyncio
import anthropic
from dotenv import load_dotenv
from agent.state import AgentState, ToolCall
from agent.budget import BudgetTracker, BudgetExceededError
from agent import planner, reflector
from tools import TOOLS_MAP

load_dotenv()

client = anthropic.Anthropic(api_key=os.getenv("ANTHROPIC_API_KEY"))

MAX_ITERATIONS = 10

ANSWER_PROMPT = """You are a helpful assistant. Given the original query and all tool observations,
produce a clear, accurate final answer. Be concise and directly answer the question.
Always include numbers or facts from the observations where relevant."""

def parse_tool_call(next_tool_text: str):
    """Parse reflector's NEXT_TOOL text into tool_name and input."""
    try:
        # Expected format: "tool_name: input text"
        parts = next_tool_text.split(":", 1)
        tool_name = parts[0].strip().lower().replace(" ", "_")
        tool_input = parts[1].strip() if len(parts) > 1 else ""
        return tool_name, tool_input
    except Exception:
        return None, None

def run_tool(tool_name: str, tool_input: str) -> ToolCall:
    """Run a single tool and return a ToolCall with observation."""
    tc = ToolCall(tool_name=tool_name, tool_input={"input": tool_input})

    if tool_name not in TOOLS_MAP:
        tc.observation = f"ERROR: Tool '{tool_name}' not found"
        tc.success = False
        return tc

    tool = TOOLS_MAP[tool_name]
    result = tool.safe_run(
        **{"query": tool_input} if tool_name in ["web_search", "knowledge_base", "document_qa"]
        else {"expression": tool_input} if tool_name == "calculator"
        else {"city": tool_input}
    )

    tc.observation = result
    tc.success = not result.startswith("ERROR")
    return tc

async def run_tool_async(tool_name: str, tool_input: str) -> ToolCall:
    """Async wrapper to run tools in parallel."""
    loop = asyncio.get_event_loop()
    return await loop.run_in_executor(None, run_tool, tool_name, tool_input)

def generate_final_answer(state: AgentState, budget: BudgetTracker) -> str:
    observations_text = "\n".join([
        f"- {tc.tool_name}: {tc.observation[:300]}"
        for tc in state.tool_calls
    ])

    response = client.messages.create(
        model="claude-haiku-4-5",
        max_tokens=500,
        system=ANSWER_PROMPT,
        messages=[{
            "role": "user",
            "content": f"Query: {state.query}\n\nObservations:\n{observations_text}"
        }]
    )

    budget.add(response.usage.input_tokens, response.usage.output_tokens)
    return response.content[0].text

async def run_agent(query: str, max_usd: float = 0.10) -> dict:
    budget = BudgetTracker(max_usd=max_usd)
    state = AgentState(query=query)

    try:
        # Step 1: Plan
        state.plan = planner.generate_plan(query, budget)
        budget.check()

        # Step 2: Initial tool calls from plan (run in parallel if possible)
        plan_lines = [
            line.strip() for line in state.plan.split("\n")
            if line.strip() and any(t in line.lower() for t in TOOLS_MAP.keys())
        ]

        if plan_lines:
            tasks = []
            for line in plan_lines[:3]:  # max 3 parallel initial calls
                for tool_name in TOOLS_MAP.keys():
                    if tool_name in line.lower():
                        # extract input — use the query as fallback
                        tasks.append(run_tool_async(tool_name, query))
                        break

            if tasks:
                results = await asyncio.gather(*tasks, return_exceptions=True)
                for result in results:
                    if isinstance(result, ToolCall):
                        state.tool_calls.append(result)

        budget.check()

        # Step 3: Reflect and iterate
        while state.iterations < MAX_ITERATIONS:
            state.iterations += 1

            reflection = reflector.reflect(state, budget)
            budget.check()

            if reflection["is_done"]:
                break

            # Tool failure recovery — try web_search as fallback
            next_tool_text = reflection.get("next_tool")
            if next_tool_text:
                tool_name, tool_input = parse_tool_call(next_tool_text)

                if tool_name and tool_name not in TOOLS_MAP:
                    # fallback to web_search
                    tool_name = "web_search"

                if tool_name:
                    tc = await run_tool_async(tool_name, tool_input or query)
                    state.tool_calls.append(tc)

                    # Retry once if tool failed
                    if not tc.success:
                        retry = await run_tool_async("web_search", query)
                        state.tool_calls.append(retry)

            budget.check()

        # Step 4: Final answer
        state.final_answer = generate_final_answer(state, budget)
        state.is_done = True

    except BudgetExceededError as e:
        state.final_answer = f"Budget limit reached: {str(e)}"
        state.error = str(e)

    except Exception as e:
        state.final_answer = f"Agent error: {str(e)}"
        state.error = str(e)

    return {
        "query": state.query,
        "plan": state.plan,
        "tool_calls": [
            {
                "tool": tc.tool_name,
                "input": tc.tool_input,
                "observation": tc.observation[:300],
                "success": tc.success
            }
            for tc in state.tool_calls
        ],
        "final_answer": state.final_answer,
        "iterations": state.iterations,
        "budget": budget.summary(),
        "is_done": state.is_done
    }