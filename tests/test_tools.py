from dotenv import load_dotenv
load_dotenv()

from tools.calculator import CalculatorTool
from tools.weather import WeatherTool
from tools.knowledge_base import KnowledgeBaseTool

def test_calculator_basic():
    tool = CalculatorTool()
    result = tool.run(expression="25 * 48")
    assert "1200" in result

def test_calculator_complex():
    tool = CalculatorTool()
    result = tool.run(expression="5000 * (1.07 ** 10)")
    assert "9835" in result or "9836" in result

def test_calculator_bad_input():
    tool = CalculatorTool()
    result = tool.safe_run(expression="not a math expression $$")
    assert "error" in result.lower() or "Error" in result

def test_weather_returns_data():
    tool = WeatherTool()
    result = tool.run(city="London")
    assert len(result) > 0
    assert "error" not in result.lower()

def test_knowledge_base_found():
    tool = KnowledgeBaseTool()
    result = tool.run(query="product")
    assert "Product X" in result

def test_knowledge_base_not_found():
    tool = KnowledgeBaseTool()
    result = tool.run(query="xyznonexistent123")
    assert "No results" in result