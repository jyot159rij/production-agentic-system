# AI Usage Note

## What Claude helped with
- Generating the initial boilerplate structure for each file
- Writing the reflector and planner prompt templates
- Suggesting simpleeval as a safe alternative to raw eval()
- Generating the 10 evaluation queries and scoring rubric

## What I wrote and decided myself
- The agent loop termination logic and MAX_ITERATIONS cap
- The decision to use Haiku 4.5 over larger models for cost reasons
- Identifying the web_search over-calling bug from eval output
- The BudgetTracker pricing correction (Claude initially gave wrong per-token rates)
- Choosing ChromaDB over Pinecone for local simplicity
- The ablation test design and interpreting the results honestly

## How I verified what AI produced
- Ran every file through the test suite before committing
- Ran the full eval suite to catch behavioural issues the code review missed
- Manually checked the budget.py pricing against Anthropic's official docs
- Read every generated file line by line before using it

## Honest assessment
Roughly 60% of the code was AI-assisted first draft, 40% was written or 
significantly modified by me. The architectural decisions, debugging, and 
evaluation analysis were entirely my own work. AI tools are fast at boilerplate 
— the judgment about what to build and whether it actually works is still human.