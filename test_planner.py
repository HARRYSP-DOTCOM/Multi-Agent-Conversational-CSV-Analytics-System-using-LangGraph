from agents.planner_agent import planner_agent


tests = [
    "when did messi last win world cup",
    "who all are the HR employees and what is the full form of HR",
    "which region had the most sales and who are the top competitiors of samsung",
    "Which region has highest sales?",
    "Latest AI news",
    "Compare uploaded revenue with current inflation trends",
    "Which stock has the highest price?",
    "What is the current market trend for the uploaded stocks?",
]


for question in tests:
    result = planner_agent(
        {
            "question": question
        }
    )

    print(
        question,
        "->",
        result["route"],
        result["route_reason"]
    )
