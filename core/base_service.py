"""
Base service interface and common service infrastructure.

Demonstrates:
- Abstract Base Class for service layer (`abc.ABC`)
- Encapsulation of service state
- Standardized logging and health check protocols
"""

import abc
import logging
from typing import Dict, Any


class BaseService(abc.ABC):
    """
    Abstract Base Class for application services (data loaders, profilers, executors).
    Enforces standardized lifecycle and status reporting.
    """

    def __init__(self, service_name: str) -> None:
        self._service_name = service_name
        self._logger = logging.getLogger(f"csv_agent.service.{service_name}")
        self._initialized = False

    @property
    def service_name(self) -> str:
        """Returns the registered name of the service."""
        return self._service_name

    @property
    def is_initialized(self) -> bool:
        """Indicates whether service is ready to handle operations."""
        return self._initialized

    @abc.abstractmethod
    def health_check(self) -> Dict[str, Any]:
        """
        Check health status and dependencies of the service.
        Must be implemented by concrete services.
        """
        raise NotImplementedError

    def __repr__(self) -> str:
        return f"{self.__class__.__name__}(service_name={self._service_name!r}, initialized={self._initialized})"

    def __str__(self) -> str:
        return f"Service[{self._service_name}]"
