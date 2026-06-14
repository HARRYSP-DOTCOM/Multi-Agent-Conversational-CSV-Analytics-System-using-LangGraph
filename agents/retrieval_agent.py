from state.agent_state import AgentState
from services.embedding_service import EmbeddingService
embedding_service = EmbeddingService()
embedding_service.load_index()
def retrieval_agent(state: AgentState):
    print("\n=== RETRIEVAL AGENT ===")
    parsed_query = state["parsed_query"]
    entities = parsed_query.get(
        "entities",
        []
    )
    if not entities:
        state["retrieval_result"] = None
        return state
    entity = entities[0]
    print("\nSearching for:")
    print(entity)
    results = embedding_service.search(
        entity,
        top_k=3
    )
    print("\nCandidates:")
    for result in results:
        print(result)
    best_match = results[0]
    state["retrieval_result"] = {
        "resolved_entity":
            best_match["value"],
        "table":
            best_match["table"],
        "column":
            best_match["column"],
        "distance":
            best_match["distance"],
        "candidates":
            results
    }
    return state