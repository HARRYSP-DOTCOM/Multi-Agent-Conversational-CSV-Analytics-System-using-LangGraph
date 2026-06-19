from agents.web_search_agent import web_search_node

state = {
    "question": "Latest inflation rate in India"
}

result = web_search_node(state)

print(result["web_result"])