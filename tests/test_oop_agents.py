"""
Unit tests verifying Object-Oriented Programming (OOP) concepts:
- Abstract Base Classes (ABC) and @abstractmethod enforcement
- Inheritance and Polymorphic dispatch
- Encapsulation and @property getters/setters
- Magic / Dunder methods (__call__, __repr__, __str__)
- Template Method Design Pattern
- Factory & Registry Design Patterns
"""

import unittest
from state.agent_state import AgentState
from core.base_agent import BaseAgent
from agents.agent_factory import AgentRegistry
import agents


class IncompleteAgent(BaseAgent):
    """Fails instantiation because abstract method `process` is not implemented."""
    pass


class DummyAgent(BaseAgent):
    """Concrete implementation of BaseAgent for testing."""

    def __init__(self, name="dummy_test_agent"):
        super().__init__(name=name, description="Testing dummy agent")

    def process(self, state: AgentState) -> AgentState:
        state["dummy_processed"] = True
        return state


class TestOOPAgents(unittest.TestCase):
    """Test suite covering Object-Oriented principles in agents."""

    def test_abstract_base_class_enforcement(self):
        """Verifies that instantiating a BaseAgent without `process` raises TypeError."""
        with self.assertRaises(TypeError):
            IncompleteAgent("incomplete")  # type: ignore

    def test_concrete_agent_inheritance_and_properties(self):
        """Verifies subclassing BaseAgent, name, and description properties."""
        agent = DummyAgent("test_worker")
        self.assertEqual(agent.name, "test_worker")
        self.assertEqual(agent.description, "Testing dummy agent")
        self.assertEqual(agent.execution_count, 0)
        self.assertEqual(agent.average_duration, 0.0)

    def test_dunder_call_and_template_method_pattern(self):
        """Verifies that calling the instance invokes the full lifecycle via `__call__`."""
        agent = DummyAgent("test_callable")
        state: AgentState = {"question": "What is the average sales?"}  # type: ignore

        # Invoke agent instance as a callable function: agent(state)
        result_state = agent(state)

        self.assertTrue(result_state.get("dummy_processed"))
        self.assertEqual(agent.execution_count, 1)
        self.assertGreater(agent.average_duration, 0.0)

        # Calling again increments executions
        agent(state)
        self.assertEqual(agent.execution_count, 2)

    def test_dunder_repr_and_str(self):
        """Verifies __repr__ and __str__ implementations."""
        agent = DummyAgent("sample_agent")
        self.assertIn("DummyAgent(name='sample_agent'", repr(agent))
        self.assertIn("Agent[sample_agent]", str(agent))

    def test_agent_registry_and_factory_pattern(self):
        """Verifies that the AgentRegistry registers, lists, and instantiates agents."""
        available = AgentRegistry.list_available_agents()
        self.assertIn("query", available)
        self.assertIn("analysis", available)
        self.assertIn("planner", available)
        self.assertIn("response", available)

        # Factory creation
        query_inst = AgentRegistry.create("query")
        self.assertIsInstance(query_inst, BaseAgent)
        self.assertEqual(query_inst.name, "query_agent")

def tearDownModule():
    """Cleanly close any background services opened during tests."""
    if hasattr(agents.history_agent, "history_service") and agents.history_agent.history_service:
        agents.history_agent.history_service.close()


if __name__ == "__main__":
    unittest.main()

