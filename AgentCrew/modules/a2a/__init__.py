"""
A2A (Agent-to-Agent) protocol implementation for SwissKnife.
This module provides a server that exposes SwissKnife agents via the A2A protocol.
"""

from .server import A2AServer
from .task_store import (
    TaskStore,
    InMemoryTaskStore,
    FileTaskStore,
    RedisTaskStore,
    create_task_store,
)

__all__ = [
    "A2AServer",
    "TaskStore",
    "InMemoryTaskStore",
    "FileTaskStore",
    "RedisTaskStore",
    "create_task_store",
]
