"""Decoupled Agent Tool Execution Loop wrapping Qwen Causal LM + LoRA weights."""
import json
import re
import logging
from typing import Dict, Any, Optional
import torch

from .tool_registry import ToolRegistry
from .memory import ConversationMemory

logger = logging.getLogger(__name__)


class Agent:
    """
    Autonomous tool-calling agent running inference on Qwen2.5-3B + LoRA checkpoints.
    Completely decoupled from the federated learning training layer.
    """

    def __init__(
        self,
        model: Any,
        tokenizer: Any,
        tool_registry: Optional[ToolRegistry] = None,
        system_prompt: str = "You are an AI assistant equipped with specialized tools. Call tools when needed.",
    ):
        self.model = model
        self.tokenizer = tokenizer
        self.tool_registry = tool_registry or ToolRegistry()
        self.memory = ConversationMemory(system_prompt=system_prompt)
        self.device = torch.device("cuda" if torch.cuda.is_available() else "cpu")

    def parse_tool_calls(self, text: str) -> list[Dict[str, Any]]:
        """
        Extract tool call requests from model output text.
        Supports Qwen <tool_call> tags and standard JSON blocks.
        """
        tool_calls = []

        # 1. Check for explicit <tool_call> tags
        pattern = r"<tool_call>\s*({.*?})\s*</tool_call>"
        matches = re.findall(pattern, text, re.DOTALL)
        for match in matches:
            try:
                data = json.loads(match)
                if "name" in data:
                    tool_calls.append(data)
            except json.JSONDecodeError:
                pass

        # 2. Fallback check for raw JSON with 'name' and 'arguments'
        if not tool_calls:
            json_pattern = r"{\s*\"name\"\s*:\s*\"[^\"]+\"\s*,\s*\"arguments\"\s*:\s*{.*?}\s*}"
            matches = re.findall(json_pattern, text, re.DOTALL)
            for match in matches:
                try:
                    data = json.loads(match)
                    tool_calls.append(data)
                except json.JSONDecodeError:
                    pass

        return tool_calls

    def _generate_response(self, prompt: str, max_new_tokens: int = 128) -> str:
        """Run PyTorch model inference or mock response for testing."""
        if hasattr(self.model, "generate") and hasattr(self.tokenizer, "encode"):
            inputs = self.tokenizer(prompt, return_tensors="pt").to(self.device)
            with torch.no_grad():
                outputs = self.model.generate(
                    **inputs,
                    max_new_tokens=max_new_tokens,
                    pad_token_id=self.tokenizer.pad_token_id,
                )
            generated_ids = outputs[0][inputs["input_ids"].shape[1]:]
            return self.tokenizer.decode(generated_ids, skip_special_tokens=True)
        
        # Mock generation fallback when running with fast linear test model
        if "status" in prompt.lower() or "server" in prompt.lower():
            return '<tool_call>{"name": "get_server_status", "arguments": {"server_id": "web-01"}}</tool_call>'
        elif "lab" in prompt.lower() or "patient" in prompt.lower():
            return '<tool_call>{"name": "get_lab_results", "arguments": {"patient_id": "P-84920"}}</tool_call>'
        elif "order" in prompt.lower() or "track" in prompt.lower():
            return '<tool_call>{"name": "track_order", "arguments": {"order_id": "ORD-99381"}}</tool_call>'
        elif "sql" in prompt.lower() or "users" in prompt.lower():
            return '<tool_call>{"name": "execute_sql", "arguments": {"query": "SELECT COUNT(*) FROM users;"}}</tool_call>'
        return "I am ready to assist you with your task."

    def run(self, user_query: str, max_turns: int = 5) -> str:
        """
        Execute full tool-calling agent loop until final response.
        """
        self.memory.add_user_message(user_query)

        for turn in range(max_turns):
            tools_schema = self.tool_registry.get_tools_schema()
            messages = self.memory.get_messages()

            if hasattr(self.tokenizer, "apply_chat_template"):
                try:
                    prompt = self.tokenizer.apply_chat_template(
                        messages,
                        tools=tools_schema,
                        tokenize=False,
                        add_generation_prompt=True,
                    )
                except Exception:
                    prompt = str(messages)
            else:
                prompt = str(messages)

            model_output = self._generate_response(prompt)
            tool_calls = self.parse_tool_calls(model_output)

            if not tool_calls:
                self.memory.add_assistant_message(model_output)
                return model_output

            # Process tool calls
            self.memory.add_assistant_message(model_output)
            for call in tool_calls:
                name = call.get("name")
                args = call.get("arguments", {})
                logger.info(f"Agent executing tool: {name}({args})")
                tool_result = self.tool_registry.execute_tool(name, args)
                self.memory.add_tool_message(name, tool_result)

        return self.memory.get_messages()[-1]["content"]
