"""
Query Agent node responsible for translating natural language into executable Python/Pandas code.

Demonstrates:
- Subclassing `BaseAgent` with polymorphic `process` method
- Callable object instance pattern for LangGraph nodes (`__call__`)
- Custom decorators (`@timing_profiler`)
- Robust error handling and state validation
"""

from typing import Optional
from state.agent_state import AgentState
from core.base_agent import BaseAgent
from core.decorators import timing_profiler
from core.enums import QueryIntent
from services.llm_service import LLMService
from services.context_service import ContextService
from agents.agent_factory import AgentRegistry


@AgentRegistry.register("query")
class QueryAgent(BaseAgent):
    """
    Translates user questions into executable pandas code via LLM.
    Inherits from `BaseAgent` to standardize execution hooks and telemetry.
    """

    def __init__(self) -> None:
        super().__init__(name="query_agent", description="Generates analytical Pandas code from natural language")
        self._llm: Optional[LLMService] = None
        self._context_service: Optional[ContextService] = None

    def _get_llm(self) -> LLMService:
        if self._llm is None:
            self._llm = LLMService()
        return self._llm

    def _get_context_service(self) -> ContextService:
        if self._context_service is None:
            self._context_service = ContextService()
        return self._context_service

    @timing_profiler(threshold_seconds=0.1)
    def process(self, state: AgentState) -> AgentState:
        """
        Executes query translation and populates `generated_code` in state.
        """
        question = state.get("csv_question") or state.get("question", "")
        self._logger.info(f"Processing query for question: {question!r}")

        context_service = self._get_context_service()
        contexts = context_service.load_contexts()

        llm = self._get_llm()
        error_message = state.get("error_message")
        previous_code = state.get("previous_code")
        retry_count = state.get("retry_count", 0)

        if error_message:
            self._logger.warning(f"[RETRY {retry_count}] Retrying generation due to error: {error_message}")
            retry_count += 1

        generated_code = llm.generate_python(
            question,
            contexts,
            error_message=error_message,
            previous_code=previous_code,
        )

        state["parsed_query"] = {
            "intent": QueryIntent.DYNAMIC.value
        }
        state["generated_code"] = generated_code
        state["retry_count"] = retry_count
        # Clear error message so it does not loop infinitely if next run succeeds
        state["error_message"] = None

        return state


# Singleton callable instance for LangGraph graph execution
query_agent = QueryAgent()
