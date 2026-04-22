import sqlite3
from tools.base import BaseTool

class KnowledgeBaseTool(BaseTool):
    name = "knowledge_base"
    description = "Look up internal company facts and product info. Input: topic or keyword as string."

    def run(self, query: str) -> str:
        try:
            conn = sqlite3.connect("knowledge_base.db")
            c = conn.cursor()
            c.execute(
                "SELECT topic, fact FROM facts WHERE topic LIKE ? OR fact LIKE ?",
                (f"%{query}%", f"%{query}%")
            )
            rows = c.fetchall()
            conn.close()

            if not rows:
                return f"No results found for: {query}"

            results = [f"[{row[0]}] {row[1]}" for row in rows]
            return "\n".join(results)
        except Exception as e:
            return f"Knowledge base error: {str(e)}"