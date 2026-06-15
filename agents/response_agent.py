from state.agent_state import AgentState


def response_agent(state: AgentState):

    print("\n=== RESPONSE AGENT ===")

    parsed = state["parsed_query"]

    analysis = state["analysis_result"]

    retrieval = state.get(
        "retrieval_result"
    )

    # ==========================================
    # Unsupported
    # ==========================================

    if analysis["type"] == "unsupported":

        response = (
            "I can answer questions "
            "related to the available datasets only."
        )

        state["final_response"] = response

        return state

    # ==========================================
    # Errors
    # ==========================================

    if analysis["type"] == "error":

        state["final_response"] = (
            analysis["message"]
        )

        return state

    # ==========================================
    # Aggregation
    # ==========================================

    if analysis["type"] == "aggregation":

        entities = parsed.get(
            "entities",
            []
        )

        original_entity = "Unknown"

        if entities:

            entity = entities[0]

            if isinstance(entity, dict):

                original_entity = entity.get(
                    "value",
                    "Unknown"
                )

            else:

                original_entity = entity

        resolved_entity = retrieval[
            "resolved_entity"
        ]

        response = (
            f'I interpreted "{original_entity}" '
            f'as "{resolved_entity}".\n\n'
            f'The {analysis["metric"]} is '
            f'{analysis["value"]:,.0f}.'
        )

        state["final_response"] = response

        return state

    # ==========================================
    # Ranking
    # ==========================================

    if analysis["type"] == "ranking":

        operation_text = (
            "highest"
            if analysis["operation"] == "max"
            else "lowest"
        )

        response = (
            f'{analysis["entity"]} '
            f'has the {operation_text} '
            f'{analysis["metric"]} of '
            f'{analysis["value"]:,.0f}.'
        )

        state["final_response"] = response

        return state

    # ==========================================
    # Count
    # ==========================================

    if analysis["type"] == "count":

        state["final_response"] = (
            f'The count is '
            f'{analysis["value"]}.'
        )

        return state

    # ==========================================
    # Comparison
    # ==========================================

    if analysis["type"] == "comparison":

        lines = [
            f'Comparison of '
            f'{analysis["metric"]}:'
        ]

        highest = None

        for item in analysis[
            "comparisons"
        ]:

            lines.append(
                f'- {item["entity"]}: '
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

        state["final_response"] = (
            "\n".join(lines)
        )

        return state

    # ==========================================
    # Filter
    # ==========================================

    if analysis["type"] == "filter":

        rows = analysis["rows"]

        if not rows:

            response = (
                "No matching records found."
            )

        else:

            response = (
                f'Found {len(rows)} '
                f'matching records:\n\n'
            )

            for row in rows:

                response += f"{row}\n"

        state["final_response"] = response

        return state

    # ==========================================
    # Fallback
    # ==========================================

    state["final_response"] = (
        "I could not generate a response."
    )

    return state