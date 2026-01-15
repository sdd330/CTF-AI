"""
Event Emitter module for publish-subscribe pattern.
Provides SocketEvent enum and EventEmitter base class.
"""

from enum import Enum
from typing import Optional, Dict, Set, Callable, Any


class SocketEvent(Enum):
    """Socket event types"""
    CONNECT = "connect"
    DISCONNECT = "disconnect"
    MESSAGE = "message"
    ERROR = "error"
    ACTIONS_RECEIVED = "actions_received"


# Event listener type alias
EventListener = Callable[..., None]


class EventEmitter:
    """
    Event emitter implementing publish-subscribe pattern.
    Provides event subscription and publishing functionality.
    """

    def __init__(self):
        """Initialize event emitter"""
        self.events: Dict[SocketEvent, Set[EventListener]] = {}

    def on(self, event: SocketEvent, listener: EventListener):
        """
        Subscribe to an event.

        Args:
            event: Event type
            listener: Event listener function
        """
        if event not in self.events:
            self.events[event] = set()
        self.events[event].add(listener)

    def off(self, event: SocketEvent, listener: EventListener):
        """
        Unsubscribe from an event.

        Args:
            event: Event type
            listener: Event listener function
        """
        if event in self.events:
            self.events[event].discard(listener)

    def emit(self, event: SocketEvent, *args, **kwargs):
        """
        Publish an event.

        Args:
            event: Event type
            *args: Positional arguments
            **kwargs: Keyword arguments
        """
        if event in self.events:
            # Copy list to avoid modification during iteration
            for listener in list(self.events[event]):
                try:
                    listener(*args, **kwargs)
                except Exception as error:
                    print(f"Error in event listener for {event.value}: {error}")

    def remove_all_listeners(self, event: Optional[SocketEvent] = None):
        """
        Remove all listeners.

        Args:
            event: If specified, only remove listeners for this event;
                   otherwise remove all listeners
        """
        if event:
            self.events.pop(event, None)
        else:
            self.events.clear()
