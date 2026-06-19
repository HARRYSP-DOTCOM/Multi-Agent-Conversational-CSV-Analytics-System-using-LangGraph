from langgraph.graph import (
    StateGraph,
    END
)
from state.agent_state import AgentState
from agents.query_agent import query_agent
from agents.retrieval_agent import retrieval_agent
from agents.analysis_agent import analysis_agent
from agents.response_agent import response_agent
from agents.planner_agent import planner_agent
from agents.web_search_agent import web_search_node

def build_graph():

    graph = StateGraph(AgentState)

    graph.add_node(
        "query",
        query_agent
    )

    graph.add_node(
        "retrieval",
        retrieval_agent
    )

    graph.add_node(
        "analysis",
        analysis_agent
    )

    graph.add_node(
        "response",
        response_agent
    )
    graph.add_node(
        "planner",
         planner_agent
    )

    graph.add_node(
        "web_search",
        web_search_node
    )

    graph.set_entry_point(
        "planner"
    )

    graph.add_edge(
        "query",
        "retrieval"
    )

    graph.add_edge(
        "retrieval",
        "analysis"
    )
    graph.add_edge(
        "web_search",
        "response"
    )

    def route_after_planner(state: AgentState):
      return state["route"]
    
    graph.add_conditional_edges(
    "planner",
    route_after_planner,
    {
        "csv": "query",
        "web": "web_search",
        "hybrid": "query"
    }
)

    def route_after_analysis(state: AgentState):
        error_message = state.get("error_message")
        retry_count = state.get("retry_count", 0)
        
        if error_message and retry_count < 3:
            return "query"
        return "response"

    graph.add_conditional_edges(
        "analysis",
        route_after_analysis,
        {
            "query": "query",
            "response": "response"
        }
    )

    graph.add_edge(
        "response",
        END
    )

    return graph.compile()