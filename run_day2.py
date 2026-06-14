from graphs.analytics_graph import (
    build_graph
)
graph = build_graph()
from graphs.analytics_graph import build_graph

graph = build_graph()

print("\n=== CSV Analytics Agent ===")
print("Type 'exit' to quit.\n")
while True:
    question = input("Ask a question: ")
    if question.lower() in ["exit", "quit"]:
        print("\nGoodbye!")
        break
    initial_state = {
        "question": question,
        "parsed_query": None,
        "retrieval_result": None,
        "analysis_result": None,
        "final_response": None
    }
    try:
        result = graph.invoke(
            initial_state
        )
        print("\n=== FINAL ANSWER ===")
        print(result["final_response"])
    except Exception as error:
        print("\nError:")
        print(error)
    print("\n" + "=" * 60 + "\n")
print("\n=== FINAL STATE ===")
print(result)