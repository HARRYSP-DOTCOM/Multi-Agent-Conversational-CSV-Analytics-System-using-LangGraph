from state.agent_state import AgentState
from services.llm_service import LLMService
from services.context_service import ContextService

_llm = None
_context_service = None


def get_llm():

    global _llm

    if _llm is None:

        print("Loading Qwen...")

        _llm = LLMService()

        print("Qwen Ready.")

    return _llm


def get_context_service():

    global _context_service

    if _context_service is None:

        _context_service = ContextService()

    return _context_service


def query_agent(state: AgentState):

    print("\n=== QUERY AGENT ===")

    question = state["question"]

    print("Question:")
    print(question)

    llm = get_llm()

    context_service = get_context_service()

    contexts = context_service.load_contexts()

    # ------------------------------------------
    # Existing JSON understanding (fallback)
    # ------------------------------------------

    parsed_query = llm.understand_query(
        question,
        contexts
    )

    print("\nParsed Query:")
    print(parsed_query)

    state["parsed_query"] = parsed_query

    # ------------------------------------------
    # NEW: Generate Python
    # ------------------------------------------

    generated_code = llm.generate_python(
        question,
        contexts
    )

    print("\nGenerated Python:")
    print(generated_code)

    state["generated_code"] = generated_code

    return state