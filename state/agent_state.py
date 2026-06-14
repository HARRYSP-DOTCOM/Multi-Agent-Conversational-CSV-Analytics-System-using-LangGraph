from typing import TypedDict, Optional
class AgentState(TypedDict):
    """
    Shared state flowing through LangGraph.
    """
    question: str
    parsed_query: Optional[dict]
    retrieval_result: Optional[dict]
    analysis_result: Optional[dict]
    final_response: Optional[str]