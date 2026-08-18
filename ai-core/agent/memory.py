"""Conversation Memory for managing dialogue history and tool outputs."""
from typing import List, Dict, Any


class ConversationMemory:
    """Manages chat messages context buffer."""

    def __init__(self, system_prompt: str = "You are a helpful assistant with access to tools."):
        self.system_prompt = system_prompt
        self.messages: List[Dict[str, Any]] = [
            {"role": "system", "content": system_prompt}
        ]

    def add_user_message(self, content: str):
        """Append user input message."""
        self.messages.append({"role": "user", "content": content})

    def add_assistant_message(self, content: str):
        """Append assistant response message."""
        self.messages.append({"role": "assistant", "content": content})

    def add_tool_message(self, tool_name: str, content: str):
        """Append tool response output message."""
        self.messages.append({
            "role": "tool",
            "name": tool_name,
            "content": content,
        })

    def clear(self):
        """Reset conversation history back to initial system prompt."""
        self.messages = [{"role": "system", "content": self.system_prompt}]

    def get_messages(self) -> List[Dict[str, Any]]:
        """Return raw message history dicts."""
        return list(self.messages)
