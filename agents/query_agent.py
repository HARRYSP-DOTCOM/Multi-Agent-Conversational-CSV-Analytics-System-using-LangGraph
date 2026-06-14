from state.agent_state import AgentState
def query_agent(state: AgentState):
    print("\n=== QUERY AGENT ===")
    print("Question:")
    print(state["question"])
    return state