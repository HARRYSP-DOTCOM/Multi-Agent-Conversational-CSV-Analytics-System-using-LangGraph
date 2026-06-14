import re
from state.agent_state import AgentState
def parse_question(question):
    question_lower = question.lower()
    parsed = {
        "metric": None,
        "entity": None,
        "operation": "retrieve"
    }
    metrics = [
        "profit",
        "revenue",
        "salary"
    ]
    for metric in metrics:

        if metric in question_lower:
            parsed["metric"] = metric.title()
            break
    match = re.search(
        r"of (.+?)(\?|$)",
        question,
        re.IGNORECASE
    )
    if match:
        parsed["entity"] = (
            match.group(1).strip()
        )
    return parsed


def query_agent(state: AgentState):
    print("\n=== QUERY AGENT ===")
    print("Question:")
    print(state["question"])
    parsed_query = parse_question(
        state["question"]
    )
    print("\nParsed Query:")
    print(parsed_query)
    state["parsed_query"] = (
        parsed_query
    )
    return state