from typing import TypedDict, Optional

class AgentState(TypedDict):
    question: str

    parsed_query: Optional[dict]

    retrieval_result: Optional[dict]

    generated_code: Optional[str]

    execution_result: Optional[dict]

    analysis_result: Optional[dict]

    final_response: Optional[object]
    
    error_message: Optional[str]
    
    retry_count: Optional[int]
    
    previous_code: Optional[str]