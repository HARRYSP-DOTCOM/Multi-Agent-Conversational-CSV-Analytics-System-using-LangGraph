from state.agent_state import AgentState
from services.llm_service import LLMService

# ==========================================
# Cached LLM
# ==========================================

_llm = None


def get_llm():

    global _llm

    if _llm is None:

        print("Loading Qwen...")

        _llm = LLMService()

        print("Qwen Ready.")

    return _llm


# ==========================================
# Query Agent
# ==========================================

def query_agent(state: AgentState):

    print("\n=== QUERY AGENT ===")

    llm = get_llm()

    question = state["question"]

    print("Question:")
    print(question)

    parsed_query = llm.understand_query(
        question
    )

    print("\nParsed Query:")
    print(parsed_query)

    state["parsed_query"] = parsed_query

    return state