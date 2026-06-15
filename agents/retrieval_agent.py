from state.agent_state import AgentState
from services.embedding_service import EmbeddingService

# ==========================================
# Configuration
# ==========================================

CONFIDENCE_THRESHOLD = 0.8

COLUMN_PRIORITY = {
    "Stock Name": 1,
    "Employee Name": 1,
    "Product": 1,
    "Ticker": 2,
    "Region": 3
}

# ==========================================
# Cached Embedding Service
# ==========================================

_embedding_service = None


def get_embedding_service():

    global _embedding_service

    if _embedding_service is None:

        print("Loading Embedding Service...")

        _embedding_service = EmbeddingService()

        _embedding_service.load_index()

        print("Embedding Service Ready.")

    return _embedding_service


# ==========================================
# Retrieval Agent
# ==========================================

def retrieval_agent(state: AgentState):

    print("\n=== RETRIEVAL AGENT ===")

    parsed_query = state["parsed_query"]

    entities = parsed_query.get(
        "entities",
        []
    )

    # ------------------------------------------
    # No entities
    # ------------------------------------------

    if not entities:

        state["retrieval_result"] = None

        return state

    entity = entities[0]

    # ------------------------------------------
    # Support both:
    # ["Reliance"]
    #
    # and
    #
    # [{"value": "Reliance"}]
    # ------------------------------------------

    if isinstance(entity, dict):

        entity_value = entity.get(
            "value",
            ""
        )

    else:

        entity_value = entity

    print("\nSearching for:")
    print(entity_value)

    embedding_service = get_embedding_service()

    results = embedding_service.search(
        entity_value,
        top_k=3
    )

    print("\nCandidates:")

    for result in results:

        print(result)

    # ------------------------------------------
    # Pick best candidate
    # ------------------------------------------

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

    # ------------------------------------------
    # Confidence threshold
    # ------------------------------------------

    if best_match["distance"] > CONFIDENCE_THRESHOLD:

        print(
            "\nLow confidence retrieval."
        )

        state["retrieval_result"] = None

        return state

    # ------------------------------------------
    # Save retrieval result
    # ------------------------------------------

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