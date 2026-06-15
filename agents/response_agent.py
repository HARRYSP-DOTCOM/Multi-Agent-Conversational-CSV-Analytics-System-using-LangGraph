from state.agent_state import AgentState


def response_agent(state: AgentState):

    print("\n=== RESPONSE AGENT ===")

    # ==========================================
    # E2B Responses
    # ==========================================

    execution_result = state.get(
        "execution_result"
    )

    if execution_result:

        state["final_response"] = (
            execution_result
        )

        return state

    # ==========================================
    # Deterministic Responses
    # ==========================================

    parsed = state["parsed_query"]

    analysis = state["analysis_result"]

    retrieval = state.get(
        "retrieval_result"
    )

    # ------------------------------------------
    # Unsupported Queries
    # ------------------------------------------

    if analysis["type"] == "unsupported":

        response = (
            "I can answer questions "
            "related to the uploaded datasets only."
        )

        print(response)

        state["final_response"] = response

        return state

    # ------------------------------------------
    # Errors
    # ------------------------------------------

    if analysis["type"] == "error":

        response = analysis["message"]

        print(response)

        state["final_response"] = response

        return state

    # ------------------------------------------
    # Aggregation
    # ------------------------------------------

    if analysis["type"] == "aggregation":

        entities = parsed.get(
            "entities",
            []
        )

        if entities:

            entity = entities[0]

            if isinstance(entity, dict):

                original_entity = entity.get(
                    "value",
                    "Unknown"
                )

            else:

                original_entity = entity

        else:

            original_entity = "Unknown"

        resolved_entity = retrieval[
            "resolved_entity"
        ]

        response = (
            f'I interpreted "{original_entity}" '
            f'as "{resolved_entity}".\n\n'
            f'The {analysis["metric"]} is '
            f'{analysis["value"]:,.0f}.'
        )

        print(response)

        state["final_response"] = response

        return state

    # ------------------------------------------
    # Ranking
    # ------------------------------------------

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

        print(response)

        state["final_response"] = response

        return state

    # ------------------------------------------
    # Count
    # ------------------------------------------

    if analysis["type"] == "count":

        response = (
            f'The count is '
            f'{analysis["value"]}.'
        )

        print(response)

        state["final_response"] = response

        return state

    # ------------------------------------------
    # Comparison
    # ------------------------------------------

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

        response = "\n".join(
            lines
        )

        print(response)

        state["final_response"] = response

        return state

    # ------------------------------------------
    # Filter
    # ------------------------------------------

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

                response += (
                    f'{row}\n'
                )

        print(response)

        state["final_response"] = response

        return state

    # ------------------------------------------
    # Fallback
    # ------------------------------------------

    response = (
        "I could not generate "
        "a response."
    )

    print(response)

    state["final_response"] = response

    return state