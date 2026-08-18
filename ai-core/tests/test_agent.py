"""Unit tests for Decoupled Agent Layer (ToolRegistry, Memory, AgentLoop)."""
import os
import sys
import pytest

core_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
if core_dir not in sys.path:
    sys.path.insert(0, core_dir)

from agent.tool_registry import ToolRegistry
from agent.memory import ConversationMemory
from agent.agent_loop import Agent
from model.llm_model import MockLLMModel, DummyTokenizer


def test_tool_registry():
    """Verify tool registration, schema generation, and execution."""
    registry = ToolRegistry()

    @registry.register(name="add_numbers", description="Add two integers together")
    def add_numbers(a: int, b: int) -> int:
        return a + b

    schemas = registry.get_tools_schema()
    assert len(schemas) == 1
    assert schemas[0]["function"]["name"] == "add_numbers"
    assert "a" in schemas[0]["function"]["parameters"]["properties"]

    result = registry.execute_tool("add_numbers", {"a": 5, "b": 7})
    assert result == "12"


def test_conversation_memory():
    """Verify memory message buffer operations."""
    memory = ConversationMemory(system_prompt="Test System")
    assert len(memory.get_messages()) == 1

    memory.add_user_message("Hello")
    memory.add_assistant_message("Hi there")
    memory.add_tool_message("get_status", "OK")

    messages = memory.get_messages()
    assert len(messages) == 4
    assert messages[1]["role"] == "user"
    assert messages[3]["role"] == "tool"


def test_agent_tool_loop():
    """Verify agent loop parses tool calls and executes tools."""
    registry = ToolRegistry()

    @registry.register(name="get_server_status", description="Get status of server")
    def get_server_status(server_id: str) -> str:
        return f"Server {server_id} is HEALTHY"

    model = MockLLMModel()
    tokenizer = DummyTokenizer()
    agent = Agent(model=model, tokenizer=tokenizer, tool_registry=registry)

    response = agent.run("Check status of web-01", max_turns=2)
    assert "HEALTHY" in str(agent.memory.get_messages())
