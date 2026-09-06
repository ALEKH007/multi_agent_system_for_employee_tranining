import logging
from typing import Dict, List, Callable, Awaitable, Any

logger = logging.getLogger(__name__)

# Registry mapping channel names to a list of async handler functions
_registry: Dict[str, List[Callable[[dict], Awaitable[Any]]]] = {}

def register_agent(channel: str):
    """
    Decorator to register an async function as an agent handler for a specific channel.
    """
    def decorator(func: Callable[[dict], Awaitable[Any]]):
        if channel not in _registry:
            _registry[channel] = []
        _registry[channel].append(func)
        logger.info(f"Registered agent handler '{func.__name__}' for channel '{channel}'")
        return func
    return decorator

def get_registry() -> Dict[str, List[Callable[[dict], Awaitable[Any]]]]:
    """Return the current agent registry."""
    return _registry
