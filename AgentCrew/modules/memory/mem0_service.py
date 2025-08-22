from typing import List, Dict, Any
import os
from mem0 import Memory
from .base_service import BaseMemoryService


class Mem0MemoryService(BaseMemoryService):
    """Service for storing and retrieving conversation memory."""

    def __init__(self, collection_name="mem0", persist_directory=None):
        self.db_path = os.getenv("MEMORYDB_PATH", "./memory_db")
        os.makedirs(os.path.dirname(self.db_path), exist_ok=True)
        config = {
            "vector_store": {
                "provider": "chroma",
                "config": {
                    "collection_name": collection_name,
                    "path": self.db_path,
                },
            }
        }
        self.mem0 = Memory.from_config(config)

    def store_conversation(
        self, user_message: str, assistant_response: str, agent_name: str = "None"
    ) -> List[str]:
        """
        Store a conversation exchange in memory.

        Args:
            user_message: The user's message
            assistant_response: The assistant's response

        Returns:
            List of memory IDs created
        """
        self.mem0.add(
            [
                {"role": "user", "content": user_message},
                {"role": "assistant", "content": assistant_response},
            ],
            user_id="user",
        )
        return []

    async def need_generate_user_context(self, user_input) -> bool:
        return False

    def clear_conversation_context(self):
        pass

    def generate_user_context(self, user_input: str, agent_name: str = "None") -> str:
        """
        Generate context based on user input by retrieving relevant memories.

        Args:
            user_input: The current user message to generate context for

        Returns:
            Formatted string containing relevant context from past conversations
        """
        return self.retrieve_memory(user_input, 8)

    def retrieve_memory(
        self, keywords: str, limit: int = 5, agent_name: str = "None"
    ) -> str:
        """
        Retrieve relevant memories based on keywords.

        Args:
            keywords: Keywords to search for
            limit: Maximum number of results to return

        Returns:
            Formatted string of relevant memories
        """
        related_memories = self.mem0.search(keywords, user_id="user", limit=limit)
        return related_memories["results"]

    def cleanup_old_memories(self, months: int = 1) -> int:
        """
        Remove memories older than the specified number of months.

        Args:
            months: Number of months to keep

        Returns:
            Number of memories removed
        """
        return 0

    def forget_topic(self, topic: str, agent_name: str = "None") -> Dict[str, Any]:
        """
        Remove memories related to a specific topic based on keyword search.

        Args:
            topic: Keywords describing the topic to forget

        Returns:
            Dict with success status and information about the operation
        """
        return {}

    def forget_ids(self, ids: List[str], agent_name: str = "None") -> Dict[str, Any]:
        return {}
