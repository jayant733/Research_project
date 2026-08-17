# packages/common/events.py
# Technical Explanation: Implements a publisher-subscriber event registry.
# Decouples printing and logging from internal engine runtimes.

from typing import Any, Callable, List


class Event:
    """A single observable event that handlers can subscribe to."""

    def __init__(self) -> None:
        self._handlers: List[Callable[..., None]] = []

    def handle(self, handler: Callable[..., None]) -> Callable[..., None]:
        """Subscribes a listener function."""
        self._handlers.append(handler)
        return handler

    def unhandle(self, handler: Callable[..., None]) -> None:
        """Unsubscribes a listener function."""
        try:
            self._handlers.remove(handler)
        except ValueError:
            pass

    def fire(self, *args: Any, **kwargs: Any) -> None:
        """Dispatches the event to all listeners."""
        for handler in self._handlers:
            handler(*args, **kwargs)


class EventSystem:
    """Registry managing global system execution events."""

    def __init__(self) -> None:
        self.on_client_init = Event()
        self.on_get_parameters = Event()
        self.on_fit_start = Event()
        self.on_fit_end = Event()
        self.on_evaluate_start = Event()
        self.on_evaluate_end = Event()
        self.on_server_start = Event()
        self.on_server_stop = Event()
        self.on_aggregate_start = Event()
        self.on_aggregate_end = Event()


# Global Event Registry Instance
events = EventSystem()
