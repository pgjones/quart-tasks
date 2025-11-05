from abc import ABCMeta, abstractmethod
from datetime import datetime


class TaskStoreABC(metaclass=ABCMeta):
    @abstractmethod
    async def startup(self) -> None:
        """A coroutine within which any setup can be done."""
        pass

    @abstractmethod
    async def get(self, key: str, default: datetime) -> datetime:
        """Get the last execution time for the task for the given
        *key* if present or the *default* if not.

        Arguments:
            key: The key to indentify the task.
            default: If no last execution for the *key* is available,
                return this default.

        Returns:
            The last execution time.
        """
        pass

    @abstractmethod
    async def set(self, key: str, executed: datetime) -> None:
        """Set the execution time for the given *key*.

        Arguments:
            key: The key to indentify the task.
            executed: The time it was executed.
        """
        pass

    @abstractmethod
    async def shutdown(self) -> None:
        """A coroutine within which any cleanup can be done."""
        pass


class MemoryStore(TaskStoreABC):
    """An in memory store of execution times."""

    def __init__(self) -> None:
        self._executions: dict[str, datetime] = {}

    async def startup(self) -> None:
        pass

    async def get(self, key: str, default: datetime) -> datetime:
        return self._executions.get(key, default)

    async def set(self, key: str, executed: datetime) -> None:
        self._executions[key] = executed

    async def shutdown(self) -> None:
        pass
