"""
Agents package for CSV Analytics Multi-Agent System.

Imports and registers all concrete agent classes in the AgentRegistry.
"""

from agents.agent_factory import AgentRegistry
from agents.query_agent import QueryAgent, query_agent
from agents.analysis_agent import AnalysisAgent, analysis_agent
from agents.planner_agent import PlannerAgent, planner_agent
from agents.response_agent import ResponseAgent, response_agent
from agents.retrieval_agent import RetrievalAgent, retrieval_agent
from agents.history_agent import HistoryAgent, history_agent
from agents.web_search_agent import WebSearchAgent, web_search_node

__all__ = [
    "AgentRegistry",
    "QueryAgent",
    "query_agent",
    "AnalysisAgent",
    "analysis_agent",
    "PlannerAgent",
    "planner_agent",
    "ResponseAgent",
    "response_agent",
    "RetrievalAgent",
    "retrieval_agent",
    "HistoryAgent",
    "history_agent",
    "WebSearchAgent",
    "web_search_node",
]
