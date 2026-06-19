from state.agent_state import AgentState
from services.llm_service import LLMService
from services.context_service import ContextService

_llm = None
_context_service = None

def get_llm():
    global _llm

    if _llm is None:
        _llm = LLMService()

    return _llm

def get_context_service():
    global _context_service

    if _context_service is None:
        _context_service = ContextService()

    return _context_service

def query_agent(state: AgentState):

    print("\n=== QUERY AGENT ===")

    question = (
        state.get("csv_question")
        or state["question"]
    )

    print("Question:")
    print(question)

    q = question.lower()

    # =====================================
    # All Queries -> E2B (Dynamic Execution)
    # =====================================

    # =====================================
    # Everything Else → E2B
    # =====================================

    print("\nUsing E2B Path")

    context_service = get_context_service()

    contexts = context_service.load_contexts()

    llm = get_llm()
    
    error_message = state.get("error_message")
    previous_code = state.get("previous_code")
    retry_count = state.get("retry_count", 0)
    
    if error_message:
        print(f"\n[RETRY {retry_count}] Retrying after error: {error_message}")
        retry_count += 1

    generated_code = llm.generate_python(
        question,
        contexts,
        error_message=error_message,
        previous_code=previous_code
    )

    print("\nGenerated Python:")
    print(generated_code)

    state["parsed_query"] = {
        "intent": "dynamic"
    }

    state["generated_code"] = generated_code
    state["retry_count"] = retry_count
    # Clear error message so it doesn't loop infinitely if next run succeeds
    state["error_message"] = None

    return state
