from services.exa_service import ExaService


_exa_service = None


def get_exa_service():
    global _exa_service

    if _exa_service is None:
        _exa_service = ExaService()

    return _exa_service


def web_search_node(state):
    question = (
        state.get("web_question")
        or state["question"]
    )

    exa_service = get_exa_service()
    results = exa_service.search(question)

    state["web_result"] = results

    return state
