from dataclasses import dataclass, field
from typing import List, Optional

@dataclass
class ToolCall:
    tool_name: str
    tool_input: dict
    observation: str = ""
    success: bool = True

@dataclass
class AgentState:
    query: str
    plan: str = ""
    tool_calls: List[ToolCall] = field(default_factory=list)
    iterations: int = 0
    final_answer: str = ""
    is_done: bool = False
    error: Optional[str] = None