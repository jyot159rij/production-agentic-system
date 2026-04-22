from tools.base import BaseTool
from simpleeval import simple_eval, EvalWithCompoundTypes

class CalculatorTool(BaseTool):
    name = "calculator"
    description = "Safely evaluate mathematical expressions. Input: a math expression as string."

    def run(self, expression: str) -> str:
        try:
            result = simple_eval(expression)
            return f"Result: {result}"
        except Exception as e:
            return f"Calculator error: {str(e)}"