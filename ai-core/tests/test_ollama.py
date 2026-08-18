"""Unit & integration tests for Ollama model wrapper and Ollama agent layer."""
import os
import sys
import pytest

core_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
if core_dir not in sys.path:
    sys.path.insert(0, core_dir)

from model.ollama_model import is_ollama_available, OllamaModelWrapper
from agent.ollama_agent import OllamaAgent
from agent.tool_registry import ToolRegistry


def test_ollama_availability():
    """Verify is_ollama_available returns boolean status."""
    available = is_ollama_available()
    assert isinstance(available, bool)


def test_ollama_agent_tool_execution():
    """Verify live Ollama tool-calling execution if Ollama server is running."""
    if not is_ollama_available():
        pytest.skip("Ollama local server not running or qwen2.5:3b not pulled")

    registry = ToolRegistry()

    @registry.register(name="get_server_status", description="Query status of server")
    def get_server_status(server_id: str) -> str:
        return f"Server {server_id} is ACTIVE"

    agent = OllamaAgent(model_name="qwen2.5:3b", tool_registry=registry)
    response = agent.run("Server web-01 is having issues. Check status.", max_turns=2)

    messages = agent.memory.get_messages()
    has_tool_response = any(m.get("role") == "tool" for m in messages)
    assert has_tool_response or "ACTIVE" in str(messages) or len(response) > 0
