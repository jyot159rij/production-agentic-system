from dotenv import load_dotenv
load_dotenv()

import asyncio
import json
import time
from agent.loop import run_agent

def score_query(result: dict, expected: dict) -> dict:
    """Score a single query result against expected criteria."""

    # Check 1: Did the agent finish successfully?
    completed = result.get("is_done", False) and not result.get("error")

    # Check 2: Were the right tools used?
    tools_used = [tc["tool"] for tc in result.get("tool_calls", [])]
    expected_tools = expected.get("expected_tools", [])
    tools_correct = any(t in tools_used for t in expected_tools)

    # Check 3: Does the answer contain expected content?
    answer = result.get("final_answer", "").lower()
    expected_contains = expected.get("expected_answer_contains", [])
    answer_correct = any(
        str(e).lower() in answer
        for e in expected_contains
    )

    # Overall pass/fail — needs to complete + answer correct
    passed = completed and answer_correct

    return {
        "id": expected["id"],
        "query": expected["query"],
        "difficulty": expected["difficulty"],
        "passed": passed,
        "completed": completed,
        "tools_used": tools_used,
        "tools_correct": tools_correct,
        "answer_correct": answer_correct,
        "final_answer": result.get("final_answer", "")[:200],
        "iterations": result.get("iterations", 0),
        "budget": result.get("budget", {}),
        "error": result.get("error")
    }

async def run_single(query_data: dict) -> dict:
    """Run a single eval query with timing."""
    start = time.time()
    try:
        result = await run_agent(query_data["query"], max_usd=0.05)
    except Exception as e:
        result = {
            "is_done": False,
            "error": str(e),
            "tool_calls": [],
            "final_answer": "",
            "iterations": 0,
            "budget": {}
        }
    elapsed = round(time.time() - start, 2)
    scored = score_query(result, query_data)
    scored["latency_seconds"] = elapsed
    return scored

async def run_eval():
    """Run full evaluation suite."""
    with open("eval/queries.json") as f:
        queries = json.load(f)

    print(f"\n{'='*60}")
    print(f"RUNNING EVALUATION — {len(queries)} queries")
    print(f"{'='*60}\n")

    results = []
    total_cost = 0.0

    for i, query_data in enumerate(queries):
        print(f"[{i+1}/{len(queries)}] {query_data['query'][:60]}...")
        result = await run_single(query_data)
        results.append(result)

        status = "✅ PASS" if result["passed"] else "❌ FAIL"
        print(f"  {status} | tools: {result['tools_used']} | latency: {result['latency_seconds']}s")
        if result["error"]:
            print(f"  ERROR: {result['error']}")

        cost = result["budget"].get("cost_usd", 0)
        total_cost += cost

        # Small delay to avoid rate limits
        await asyncio.sleep(1)

    # Summary stats
    passed = sum(1 for r in results if r["passed"])
    success_rate = round(passed / len(results) * 100, 1)

    easy = [r for r in results if r["difficulty"] == "easy"]
    medium = [r for r in results if r["difficulty"] == "medium"]
    hard = [r for r in results if r["difficulty"] == "hard"]

    avg_latency = round(
        sum(r["latency_seconds"] for r in results) / len(results), 2
    )

    print(f"\n{'='*60}")
    print(f"EVALUATION RESULTS")
    print(f"{'='*60}")
    print(f"Overall Success Rate : {passed}/{len(results)} ({success_rate}%)")
    print(f"Easy queries         : {sum(1 for r in easy if r['passed'])}/{len(easy)} passed")
    print(f"Medium queries       : {sum(1 for r in medium if r['passed'])}/{len(medium)} passed")
    print(f"Hard queries         : {sum(1 for r in hard if r['passed'])}/{len(hard)} passed")
    print(f"Avg latency          : {avg_latency}s per query")
    print(f"Total cost           : ${round(total_cost, 6)}")
    print(f"{'='*60}\n")

    # Failed queries — honest reporting
    failed = [r for r in results if not r["passed"]]
    if failed:
        print("FAILED QUERIES (be honest in your report):")
        for r in failed:
            print(f"  - Q{r['id']}: {r['query'][:60]}")
            print(f"    Tools used: {r['tools_used']}")
            print(f"    Answer: {r['final_answer'][:100]}")
            print()

    # Save results to file
    with open("eval/results.json", "w") as f:
        json.dump({
            "summary": {
                "total": len(results),
                "passed": passed,
                "success_rate_pct": success_rate,
                "avg_latency_seconds": avg_latency,
                "total_cost_usd": round(total_cost, 6)
            },
            "results": results
        }, f, indent=2)

    print("Full results saved to eval/results.json")
    return results

if __name__ == "__main__":
    asyncio.run(run_eval())