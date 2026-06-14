from graphs.analytics_graph import (
    build_graph
)
graph = build_graph()
initial_state = {
    "question":
        "What is the profit of Reliance?",
    "parsed_query": None,
    "retrieval_result": None,
    "analysis_result": None,
    "final_response": None
}
result = graph.invoke(
    initial_state
)
print("\n=== FINAL STATE ===")
print(result)