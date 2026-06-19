from services.exa_service import ExaService
exa_service = ExaService()
def web_search_node(state):
    question = state["question"]
    results = exa_service.search(question)
    state["web_result"] = results
    return state