from state.agent_state import AgentState
from services.llm_service import LLMService


def _get_web_results(web_result):
    if hasattr(web_result, "results"):
        return web_result.results

    if isinstance(web_result, dict):
        return web_result.get(
            "results",
            []
        )

    return []


def _format_web_context(web_result, limit=5):
    results = _get_web_results(web_result)
    lines = []

    for i, item in enumerate(
        results[:limit],
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

        lines.append(
            f"{i}. {title}\n{url}\n{text[:700]}"
        )

    return "\n\n".join(lines)


def _fallback_web_response(web_result):
    results = _get_web_results(web_result)
    response = ""

    for i, item in enumerate(
        results[:5],
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

    return response


def _set_text_response(state, text):
    state["final_response"] = {
        "type": "text",
        "data": text
    }

    return state


def _handle_hybrid_response(state, execution_result, web_result):
    web_context = _format_web_context(
        web_result
    )

    if not web_context:
        web_context = "No web results found."

    csv_result = execution_result
    if isinstance(execution_result, dict):
        csv_result = execution_result.get("data", execution_result)

    llm = LLMService()
    summary = llm.format_hybrid_response(
        state["question"],
        str(csv_result),
        web_context
    )

    return _set_text_response(
        state,
        summary
    )


def _handle_csv_execution_response(state, execution_result):
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

    state["final_response"] = execution_result

    return state


def _handle_web_response(state, web_result):
    results = _get_web_results(
        web_result
    )

    if not results:
        return _set_text_response(
            state,
            "No web results found."
        )

    web_context = _format_web_context(
        web_result
    )

    try:
        llm = LLMService()
        response = llm.format_web_response(
            state["question"],
            web_context
        )
    except Exception:
        response = _fallback_web_response(
            web_result
        )

    return _set_text_response(
        state,
        response
    )


def _handle_deterministic_response(state):
    parsed = state.get(
        "parsed_query"
    )
    analysis = state.get(
        "analysis_result"
    )
    retrieval = state.get(
        "retrieval_result"
    )

    if analysis is None:
        state["final_response"] = "I could not generate a response."
        return state

    if analysis["type"] == "unsupported":
        state["final_response"] = (
            "I can answer questions related to the uploaded datasets only."
        )
        return state

    if analysis["type"] == "error":
        state["final_response"] = analysis["message"]
        return state

    if analysis["type"] == "aggregation":
        entities = parsed.get(
            "entities",
            []
        ) if parsed else []

        original_entity = "Unknown"

        if entities:
            entity = entities[0]
            original_entity = (
                entity.get(
                    "value",
                    "Unknown"
                )
                if isinstance(entity, dict)
                else entity
            )

        resolved_entity = (
            retrieval["resolved_entity"]
            if retrieval
            else "Unknown"
        )

        state["final_response"] = (
            f'I interpreted "{original_entity}" as '
            f'"{resolved_entity}".\n\n'
            f'The {analysis["metric"]} is '
            f'{analysis["value"]:,.0f}.'
        )

        return state

    if analysis["type"] == "ranking":
        operation_text = (
            "highest"
            if analysis["operation"] == "max"
            else "lowest"
        )

        state["final_response"] = (
            f'{analysis["entity"]} has the {operation_text} '
            f'{analysis["metric"]} of {analysis["value"]:,.0f}.'
        )

        return state

    if analysis["type"] == "count":
        state["final_response"] = (
            f'The count is {analysis["value"]}.'
        )

        return state

    if analysis["type"] == "comparison":
        lines = [
            f'Comparison of {analysis["metric"]}:'
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
                f'\nHighest: {highest_item["entity"]}'
            )

        state["final_response"] = "\n".join(
            lines
        )

        return state

    if analysis["type"] == "filter":
        rows = analysis["rows"]

        if not rows:
            state["final_response"] = "No matching records found."
            return state

        response = (
            f'Found {len(rows)} matching records:\n\n'
        )

        for row in rows:
            response += f'{row}\n'

        state["final_response"] = response

        return state

    state["final_response"] = "I could not generate a response."

    return state


def response_agent(state: AgentState):
    print("\n=== RESPONSE AGENT ===")

    route = state.get("route")
    execution_result = state.get(
        "execution_result"
    )
    web_result = state.get(
        "web_result"
    )

    try:
        if route == "hybrid" and (
            execution_result
            or web_result
        ):
            return _handle_hybrid_response(
                state,
                execution_result,
                web_result
            )

        if execution_result:
            return _handle_csv_execution_response(
                state,
                execution_result
            )

        if web_result:
            return _handle_web_response(
                state,
                web_result
            )

        return _handle_deterministic_response(
            state
        )

    except Exception as error:
        state["final_response"] = {
            "type": "error",
            "data": str(error)
        }

        return state
