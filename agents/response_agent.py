from state.agent_state import AgentState


def response_agent(state: AgentState):

    print("\n=== RESPONSE AGENT ===")

    analysis = state["analysis_result"]

    parsed = state["parsed_query"]

    retrieval = state.get(
        "retrieval_result"
    )

    # ==========================================
    # Error
    # ==========================================
    if analysis["type"] == "error":

        response = analysis["message"]

    # ==========================================
    # Aggregation
    # ==========================================
    elif analysis["type"] == "aggregation":

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

        response = (

            f'I interpreted "{original_entity}" '
            f'as "{resolved_entity}".\n\n'

            f'The {analysis["metric"]} is '

            f'{analysis["value"]:,.0f}.'
        )

    # ==========================================
    # Ranking
    # ==========================================
    elif analysis["type"] == "ranking":

        operation = analysis["operation"]

        operation_text = (

            "highest"
            if operation == "max"
            else "lowest"
        )

        response = (

            f'{analysis["entity"]} '

            f'has the {operation_text} '

            f'{analysis["metric"]} '

            f'of '

            f'{analysis["value"]:,.0f}.'
        )

    # ==========================================
    # Count
    # ==========================================
    elif analysis["type"] == "count":

        response = (

            f'The count is '

            f'{analysis["value"]}.'
        )

    # ==========================================
    # Comparison
    # ==========================================
    elif analysis["type"] == "comparison":

        lines = [

            f'Comparison of '

            f'{analysis["metric"]}:'
        ]

        highest = None

        for item in analysis["comparisons"]:

            lines.append(

                f'{item["entity"]}: '

                f'{item["value"]:,.0f}'
            )

            if (

                highest is None

                or

                item["value"]
                >
                highest["value"]

            ):

                highest = item

        if highest:

            lines.append(
                f'\nHighest: '
                f'{highest["entity"]}'
            )

        response = "\n".join(lines)

    # ==========================================
    # Filter
    # ==========================================
    elif analysis["type"] == "filter":

        rows = analysis["rows"]

        if not rows:

            response = (
                "No matching records found."
            )

        else:

            response = (

                f'Found '

                f'{len(rows)} '

                f'matching records.\n\n'

                f'{rows}'
            )

    # ==========================================
    # Fallback
    # ==========================================
    else:

        response = (
            "I could not generate a response."
        )

    print(response)

    state["final_response"] = response

    return state