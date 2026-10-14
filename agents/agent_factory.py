"""
Agent Factory demonstrating the Factory and Registry design patterns in Python.

Demonstrates:
- Factory Method Pattern
- Registry Pattern with dynamic class lookup
- Introspection with `issubclass` and `inspect`
- Metaprogramming / dynamic instantiation
"""

from typing import Dict, Type, Optional, List
from core.base_agent import BaseAgent
from core.exceptions import ConfigurationError


class AgentRegistry:
    """
    Central registry for discovering and creating agent instances.
    Implements the Registry and Factory patterns.
    """

    _registry: Dict[str, Type[BaseAgent]] = {}

    @classmethod
    def register(cls, name: str) -> callable:
        """
        Class decorator to register an agent class into the factory registry.
        """
        def decorator(subclass: Type[BaseAgent]) -> Type[BaseAgent]:
            if not issubclass(subclass, BaseAgent):
                raise TypeError(f"Registered class '{subclass.__name__}' must inherit from BaseAgent.")
            cls._registry[name.lower()] = subclass
            return subclass

        return decorator

    @classmethod
    def get_agent_class(cls, name: str) -> Type[BaseAgent]:
        """Lookup an agent class by name."""
        key = name.lower()
        if key not in cls._registry:
            raise ConfigurationError(f"Agent '{name}' is not registered in AgentRegistry. Available: {list(cls._registry.keys())}")
        return cls._registry[key]

    @classmethod
    def create(cls, name: str, *args, **kwargs) -> BaseAgent:
        """
        Factory method instantiating the requested agent.
        """
        agent_cls = cls.get_agent_class(name)
        return agent_cls(*args, **kwargs)

    @classmethod
    def list_available_agents(cls) -> List[str]:
        """Returns sorted list of registered agent names."""
        return sorted(cls._registry.keys())
