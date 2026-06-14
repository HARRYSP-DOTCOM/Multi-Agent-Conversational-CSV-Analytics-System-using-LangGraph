from state.agent_state import AgentState
from services.llm_service import (
    LLMService
)
from services.context_service import (
    ContextService
)
llm = LLMService()
context_service = ContextService()
contexts = context_service.load_contexts()

def query_agent(state: AgentState):
    print("\n=== QUERY AGENT ===")
    print("Question:")
    print(state["question"])
    parsed_query = llm.understand_query(
        state["question"],
        contexts
    )
    print("\nParsed Query:")
    print(parsed_query)
    state["parsed_query"] = parsed_query
    return state
