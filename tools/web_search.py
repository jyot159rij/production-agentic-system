import os
from tavily import TavilyClient
from tools.base import BaseTool

class WebSearchTool(BaseTool):
    name = "web_search"
    description = "Search the web for current information. Input: search query as string."

    def __init__(self):
        self.client = TavilyClient(api_key=os.getenv("TAVILY_API_KEY"))

    def run(self, query: str) -> str:
        try:
            result = self.client.search(query, max_results=3)
            outputs = []
            for r in result["results"]:
                outputs.append(f"- {r['title']}: {r['content'][:300]}")
            return "\n".join(outputs)
        except Exception as e:
            return f"Web search error: {str(e)}"