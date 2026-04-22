from dotenv import load_dotenv
load_dotenv()

import asyncio
from agent.loop import run_agent

result = asyncio.run(run_agent('What is 25 multiplied by 48?'))
print("PLAN:", result)
print("PLAN:", result['plan'])
print("ANSWER:", result['final_answer'])
print("BUDGET:", result['budget'])