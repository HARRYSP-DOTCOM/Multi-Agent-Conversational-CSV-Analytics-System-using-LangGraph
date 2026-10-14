"""
Web Search Agent node for external internet retrieval.

Demonstrates:
- Subclassing `BaseAgent`
- Dynamic registration in `AgentRegistry`
- Lazy singleton service initialization
"""

from state.agent_state import AgentState
from services.exa_service import ExaService
from core.base_agent import BaseAgent
from agents.agent_factory import AgentRegistry

_exa_service = None


def get_exa_service():
    global _exa_service
    if _exa_service is None:
        _exa_service = ExaService()
    return _exa_service


@AgentRegistry.register("web_search")
class WebSearchAgent(BaseAgent):
    """
    Executes live web search queries via Exa search API.
    Subclasses BaseAgent and registers with AgentRegistry.
    """

    def __init__(self) -> None:
        super().__init__(name="web_search_agent", description="Performs external web searches for real-time information")

    def process(self, state: AgentState) -> AgentState:
        question = (
            state.get("web_question")
            or state["question"]
        )

        exa_service = get_exa_service()
        results = exa_service.search(question)

        state["web_result"] = results
        return state


# Singleton callable instance for LangGraph graph execution
web_search_node = WebSearchAgent()
