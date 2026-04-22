from tools.calculator import CalculatorTool
from tools.weather import WeatherTool
from tools.web_search import WebSearchTool
from tools.knowledge_base import KnowledgeBaseTool
from tools.document_qa import DocumentQATool

ALL_TOOLS = [
    CalculatorTool(),
    WeatherTool(),
    WebSearchTool(),
    KnowledgeBaseTool(),
    DocumentQATool(),
]

TOOLS_MAP = {tool.name: tool for tool in ALL_TOOLS}