from state.agent_state import AgentState


def response_agent(state: AgentState):

    print("\n=== RESPONSE AGENT ===")

    parsed = state["parsed_query"]

    retrieval = state["retrieval_result"]

    analysis = state["analysis_result"]

    entities = parsed.get(
        "entities",
        []
    )

    original_entity = (
        entities[0]
        if entities
        else "Unknown"
    )

    resolved_entity = (
        retrieval["resolved_entity"]
        if retrieval
        else original_entity
    )

    metric = analysis.get(
        "metric",
        "Value"
    )

    value = analysis.get(
        "value",
        None
    )

    if value is None:

        response = (
            "I could not compute an answer."
        )

    else:

        formatted_value = f"{value:,.0f}"

        response = (
            f'I interpreted "{original_entity}" '
            f'as "{resolved_entity}".\n\n'
            f'The {metric} is '
            f'{formatted_value}.'
        )

    print(response)

    state["final_response"] = response

    return state