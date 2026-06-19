from agents.planner_agent import planner_agent

tests = [
    "Which region has highest sales?",
    "Latest AI news",
    "Compare uploaded revenue with current inflation trends"
]

for question in tests:
    result = planner_agent(
        {"question": question}
    )

    print(
        question,
        "→",
        result["route"]
    )