from langgraph.graph import (
    StateGraph,
    END
)
from state.agent_state import AgentState
from agents.query_agent import query_agent
from agents.retrieval_agent import retrieval_agent
from agents.analysis_agent import analysis_agent
from agents.response_agent import response_agent

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

    graph.set_entry_point(
        "query"
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
        "analysis",
        "response"
    )

    graph.add_edge(
        "response",
        END
    )

    return graph.compile()