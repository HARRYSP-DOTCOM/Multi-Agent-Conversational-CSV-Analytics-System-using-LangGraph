from state.agent_state import AgentState
from services.llm_service import LLMService


def response_agent(state: AgentState):

    print("\n=== RESPONSE AGENT ===")

    # ==========================================
    # E2B Responses (Current Main Flow)
    # ==========================================

    execution_result = state.get(
        "execution_result"
    )

    if execution_result:

        if isinstance(execution_result, dict):

            res_data = execution_result.get(
                "data"
            )

            llm = LLMService()

            summary = llm.format_response(
                state["question"],
                str(res_data)
            )

            execution_result["summary"] = summary

        state["final_response"] = (
            execution_result
        )

        return state

    # ==========================================
    # WEB RESPONSES (NEW)
    # ==========================================

    web_result = state.get(
        "web_result"
    )

    if web_result:

        try:

            response = ""

            # Exa SearchResponse object
            if hasattr(web_result, "results"):

                results = web_result.results

            # Dictionary fallback
            elif isinstance(web_result, dict):

                results = web_result.get(
                    "results",
                    []
                )

            else:

                results = []

            if not results:

                state["final_response"] = {
                    "type": "text",
                    "data": "No web results found."
                }

                return state

            for i, item in enumerate(
                results[:3],
                start=1
            ):

                title = getattr(
                    item,
                    "title",
                    "No Title"
                )

                url = getattr(
                    item,
                    "url",
                    "No URL"
                )

                text = getattr(
                    item,
                    "text",
                    ""
                )

                response += (
                    f"### {i}. {title}\n"
                    f"{url}\n\n"
                    f"{text[:300]}...\n\n"
                )

            state["final_response"] = {
                "type": "text",
                "data": response
            }

            return state

        except Exception as error:

            state["final_response"] = {
                "type": "error",
                "data": str(error)
            }

            return state

    # ==========================================
    # Deterministic Responses (Old Path)
    # ==========================================

    parsed = state.get(
        "parsed_query"
    )

    analysis = state.get(
        "analysis_result"
    )

    retrieval = state.get(
        "retrieval_result"
    )

    # If analysis is missing entirely
    if analysis is None:

        response = (
            "I could not generate a response."
        )

        print(response)

        state["final_response"] = response

        return state

    # ==========================================
    # Unsupported Queries
    # ==========================================

    if analysis["type"] == "unsupported":

        response = (
            "I can answer questions "
            "related to the uploaded datasets only."
        )

        print(response)

        state["final_response"] = response

        return state

    # ==========================================
    # Errors
    # ==========================================

    if analysis["type"] == "error":

        response = analysis["message"]

        print(response)

        state["final_response"] = response

        return state

    # ==========================================
    # Aggregation
    # ==========================================

    if analysis["type"] == "aggregation":

        entities = parsed.get(
            "entities",
            []
        ) if parsed else []

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
        ] if retrieval else "Unknown"

        response = (
            f'I interpreted "{original_entity}" '
            f'as "{resolved_entity}".\n\n'
            f'The {analysis["metric"]} is '
            f'{analysis["value"]:,.0f}.'
        )

        print(response)

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

        print(response)

        state["final_response"] = response

        return state

    # ==========================================
    # Count
    # ==========================================

    if analysis["type"] == "count":

        response = (
            f'The count is '
            f'{analysis["value"]}.'
        )

        print(response)

        state["final_response"] = response

        return state

    # ==========================================
    # Comparison
    # ==========================================

    if analysis["type"] == "comparison":

        lines = [
            f'Comparison of '
            f'{analysis["metric"]}:'
        ]

        if analysis.get("comparisons"):

            for item in analysis[
                "comparisons"
            ]:

                lines.append(
                    f'- {item["entity"]}: '
                    f'{item["value"]:,.0f}'
                )

            highest_item = max(
                analysis["comparisons"],
                key=lambda x: x["value"]
            )

            lines.append(
                f'\nHighest: '
                f'{highest_item["entity"]}'
            )

        response = "\n".join(
            lines
        )

        print(response)

        state["final_response"] = response

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

                response += (
                    f'{row}\n'
                )

        print(response)

        state["final_response"] = response

        return state

    # ==========================================
    # Fallback
    # ==========================================

    response = (
        "I could not generate "
        "a response."
    )

    print(response)

    state["final_response"] = response

    return state