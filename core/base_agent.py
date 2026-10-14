"""
Abstract Base Agent architecture establishing the polymorphic interface for LangGraph nodes.

Demonstrates:
- Abstract Base Classes (`abc.ABC` and `@abstractmethod`)
- Polymorphism & Interface Segregation
- Template Method Pattern (`__call__` orchestrates before -> process -> after)
- Callable object protocol (`__call__`) enabling agent instances to be invoked directly by LangGraph
- Encapsulation (`_execution_count`, `_total_duration`)
- Managed attributes with `@property`
- Magic/Dunder methods (`__repr__`, `__str__`, `__call__`)
"""

import abc
import time
import logging
from typing import Optional, Dict, Any
from state.agent_state import AgentState
from core.exceptions import AgentExecutionError

logger = logging.getLogger("csv_agent.agents")


class BaseAgent(abc.ABC):
    """
    Abstract Base Class for all workflow agents.

    Subclasses must implement the abstract `process` method.
    The Template Method Pattern is implemented in `__call__`, which manages:
    - Pre-execution validation and state snapshots
    - High-precision execution timing
    - Concrete agent execution via polymorphic dispatch
    - Post-execution bookkeeping and metric tracking
    - Exception standardization
    """

    def __init__(self, name: str, description: Optional[str] = None) -> None:
        self._name = name
        self._description = description or f"{name} agent component"
        self._execution_count = 0
        self._total_duration = 0.0
        self._logger = logging.getLogger(f"csv_agent.agent.{name}")

    # --- Properties ---

    @property
    def name(self) -> str:
        """Returns the registered name of the agent."""
        return self._name

    @property
    def description(self) -> str:
        """Returns the human-readable description of the agent."""
        return self._description

    @property
    def execution_count(self) -> int:
        """Returns the total number of times this agent has run."""
        return self._execution_count

    @property
    def average_duration(self) -> float:
        """Calculates average execution latency in seconds."""
        if self._execution_count == 0:
            return 0.0
        return self._total_duration / self._execution_count

    # --- Abstract Method (Must be implemented by concrete subclasses) ---

    @abc.abstractmethod
    def process(self, state: AgentState) -> AgentState:
        """
        Core logic of the agent. Must be overridden by subclasses.

        Args:
            state: Current LangGraph shared state dictionary.

        Returns:
            Updated AgentState dictionary.
        """
        raise NotImplementedError("Subclasses must implement the 'process' method.")

    # --- Template Method Lifecycle Hooks ---

    def before_run(self, state: AgentState) -> None:
        """Hook executed immediately before `process`. Can be overridden by subclasses."""
        self._logger.info(f"===> [{self._name.upper()}] Starting execution (Invocation #{self._execution_count + 1})")

    def after_run(self, state: AgentState, duration: float) -> None:
        """Hook executed immediately after `process`. Can be overridden by subclasses."""
        self._logger.info(f"<=== [{self._name.upper()}] Completed in {duration:.4f}s")

    # --- Callable Object Protocol (Template Method Pattern) ---

    def __call__(self, state: AgentState) -> AgentState:
        """
        Makes the class instance callable.
        LangGraph nodes accept callables of signature `f(state) -> state`.

        This coordinates the full lifecycle:
        1. before_run()
        2. process() with execution timing
        3. after_run()
        4. exception trapping & telemetry
        """
        self._execution_count += 1
        self.before_run(state)

        start_time = time.perf_counter()
        try:
            result_state = self.process(state)
        except Exception as exc:
            self._logger.error(f"[{self._name}] Encountered unhandled exception: {exc}", exc_info=True)
            if not isinstance(exc, AgentExecutionError):
                # Wrap unexpected exceptions into our domain hierarchy
                raise AgentExecutionError(
                    message=f"Agent '{self._name}' failed with {exc.__class__.__name__}: {exc}",
                    agent_name=self._name,
                    details={"original_exception": str(exc)},
                ) from exc
            raise
        finally:
            elapsed = time.perf_counter() - start_time
            self._total_duration += elapsed
            self.after_run(state, elapsed)

        return result_state

    # --- Dunder Methods ---

    def __repr__(self) -> str:
        return (
            f"{self.__class__.__name__}(name={self._name!r}, "
            f"executions={self._execution_count}, avg_time={self.average_duration:.4f}s)"
        )

    def __str__(self) -> str:
        return f"Agent[{self._name}] - {self._description}"

    def get_metrics(self) -> Dict[str, Any]:
        """Returns runtime performance statistics for telemetry."""
        return {
            "name": self._name,
            "invocations": self._execution_count,
            "total_duration_sec": round(self._total_duration, 4),
            "avg_duration_sec": round(self.average_duration, 4),
        }
