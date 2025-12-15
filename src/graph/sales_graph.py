from typing import TypedDict, Any


class AgentState(TypedDict):
    query: str
    sql: str
    result: Any
    explanation: str
