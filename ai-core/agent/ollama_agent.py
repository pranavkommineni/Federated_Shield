"""Ollama Agent implementation for live local tool calling via Ollama API."""
import json
import logging
from typing import Dict, Any, List, Optional
from .tool_registry import ToolRegistry
from .memory import ConversationMemory
from model.ollama_model import OllamaModelWrapper, DEFAULT_OLLAMA_HOST, DEFAULT_OLLAMA_MODEL

logger = logging.getLogger(__name__)


class OllamaAgent:
    """
    Autonomous tool-calling agent using local Ollama model (e.g. qwen2.5:3b).
    Communicates via Ollama's native HTTP tool-calling API.
    """

    def __init__(
        self,
        model_name: str = DEFAULT_OLLAMA_MODEL,
        host: str = DEFAULT_OLLAMA_HOST,
        tool_registry: Optional[ToolRegistry] = None,
        system_prompt: str = "You are a helpful AI assistant equipped with tools. Always use available tools to answer queries when applicable.",
    ):
        self.ollama = OllamaModelWrapper(model_name=model_name, host=host)
        self.tool_registry = tool_registry or ToolRegistry()
        self.memory = ConversationMemory(system_prompt=system_prompt)

    def run(self, user_query: str, max_turns: int = 5) -> str:
        """Execute tool-calling agent loop via Ollama chat API."""
        self.memory.add_user_message(user_query)

        for turn in range(max_turns):
            tools_schema = self.tool_registry.get_tools_schema()
            messages = self.memory.get_messages()

            logger.info(f"Sending prompt to Ollama ({self.ollama.model_name}) turn {turn + 1}...")
            response = self.ollama.chat(messages=messages, tools=tools_schema if tools_schema else None)
            
            message = response.get("message", {})
            content = message.get("content", "")
            tool_calls = message.get("tool_calls", [])

            if not tool_calls:
                self.memory.add_assistant_message(content)
                return content

            # Append assistant's tool-call response to memory
            self.memory.messages.append(message)

            # Process each requested tool call
            for call in tool_calls:
                func_data = call.get("function", {})
                name = func_data.get("name")
                args = func_data.get("arguments", {})
                logger.info(f"Ollama requested tool: '{name}' with args: {args}")

                result = self.tool_registry.execute_tool(name, args)
                logger.info(f"Tool '{name}' execution result: {result}")
                
                # Append tool execution result back into conversation
                self.memory.add_tool_message(tool_name=name, content=str(result))

        return self.memory.get_messages()[-1].get("content", "")
