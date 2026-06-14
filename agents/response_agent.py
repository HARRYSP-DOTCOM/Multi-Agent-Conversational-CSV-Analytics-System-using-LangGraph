from state.agent_state import AgentState
def response_agent(state: AgentState):
    print("\n=== RESPONSE AGENT ===")
    parsed = state["parsed_query"]
    retrieval = state["retrieval_result"]
    analysis = state["analysis_result"]
    original_entity = parsed["entity"]
    resolved_entity = (
        retrieval["resolved_entity"]
    )
    metric = analysis["metric"]
    value = analysis["value"]

    formatted_value = (
        f"{value:,.0f}"
    )

    response = (
        f'I interpreted "{original_entity}" '
        f'as "{resolved_entity}  ".'
        f'The {metric} is '
        f'{formatted_value}.'
    )
    print(response)        

    state["final_response"] = (
        response
    )
    return state