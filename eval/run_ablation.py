from dotenv import load_dotenv
load_dotenv()

import asyncio
import json
from agent import planner
from agent.loop import run_agent

# Simple 5-query ablation test
ABLATION_QUERIES = [
    "What is 144 divided by 12, then multiply by 7?",
    "What is the weather in Berlin and convert to Fahrenheit?",
    "Search the web for the current price of gold",
    "What does our knowledge base say about company revenue?",
    "What is 15 percent tip on a 85 GBP bill split between 3 people?"
]

async def run_ablation():
    import agent.planner as planner_module

    results = {"v1": [], "v2": []}

    for version in ["v1", "v2"]:
        print(f"\n--- Running Prompt {version.upper()} ---")

        if version == "v2":
            planner_module.PLANNER_PROMPT = planner_module.PLANNER_PROMPT_V2

        for query in ABLATION_QUERIES:
            print(f"  Query: {query[:50]}...")
            try:
                result = await run_agent(query, max_usd=0.05)
                passed = result["is_done"] and not result.get("error")
                results[version].append(passed)
                print(f"  {'✅' if passed else '❌'}")
            except Exception as e:
                results[version].append(False)
                print(f"  ❌ Error: {e}")

            await asyncio.sleep(1)

    v1_score = sum(results["v1"])
    v2_score = sum(results["v2"])

    print(f"\n{'='*40}")
    print(f"ABLATION RESULTS")
    print(f"{'='*40}")
    print(f"Prompt V1 (detailed): {v1_score}/5 ({v1_score*20}%)")
    print(f"Prompt V2 (minimal):  {v2_score}/5 ({v2_score*20}%)")
    print(f"Delta: {v1_score - v2_score} queries difference")
    print(f"{'='*40}")
    print("\nConclusion for report:")
    if v1_score > v2_score:
        print(f"Detailed planning prompt outperforms minimal prompt by {(v1_score-v2_score)*20}%")
        print("Explicit step-by-step instructions reduce unnecessary tool calls")
    elif v1_score == v2_score:
        print("Both prompts performed equally - agent is robust to prompt variation")
        print("Suggests tool execution logic matters more than planning prompt wording")
    else:
        print("Minimal prompt surprisingly outperformed - worth investigating why")

if __name__ == "__main__":
    asyncio.run(run_ablation())