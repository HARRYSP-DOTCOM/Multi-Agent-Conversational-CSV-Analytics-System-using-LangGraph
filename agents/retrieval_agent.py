from state.agent_state import AgentState
from services.embedding_service import EmbeddingService
embedding_service = EmbeddingService()
embedding_service.load_index()
CONFIDENCE_THRESHOLD = 0.8
COLUMN_PRIORITY = {
    "Stock Name": 1,
    "Employee Name": 1,
    "Product": 1,
    "Ticker": 2,
    "Region": 3
}
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
    if isinstance(entity, dict):
       entity_value = entity.get(
        "value",
        ""
    )
    else:
     entity_value = entity
    print("\nSearching for:")
    print(entity_value)
    results = embedding_service.search(
     entity_value,
     top_k=3
)
    print("\nCandidates:")
    for result in results:
        print(result)
    best_match = sorted(
    results,
    key=lambda r: (
        COLUMN_PRIORITY.get(
            r["column"],
            999
        ),
        r["distance"]
    )
)[0]
    if best_match["distance"] > CONFIDENCE_THRESHOLD:
     state["retrieval_result"] = None
     return state
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