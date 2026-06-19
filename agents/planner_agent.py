from typing import Literal


def planner_agent(state):
    question = state["question"].lower()

    web_keywords = [
        "latest",
        "today",
        "current",
        "news",
        "recent",
        "trend",
        "trends",
        "market",
        "weather",
        "stock",
        "inflation",
        "price"
    ]

    csv_keywords = [
        "dataset",
        "csv",
        "uploaded",
        "table",
        "column"
    ]

    has_web = any(
        keyword in question
        for keyword in web_keywords
    )

    has_csv = any(
        keyword in question
        for keyword in csv_keywords
    )

    if has_web and has_csv:
        route: Literal["hybrid"] = "hybrid"

    elif has_web:
        route = "web"

    else:
        route = "csv"

    state["route"] = route

    return state