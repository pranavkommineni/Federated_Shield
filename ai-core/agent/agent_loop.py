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
    Autonomous tool-calling agent running inference on Qwen2.5 LLM.
    Generates real LLM responses and decides tool calls based on model output.
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

    def _generate_response(self, prompt: str, max_new_tokens: int = 512) -> str:
        """Run real PyTorch model inference to generate a response."""
        # If model has a .chat() method (e.g. OllamaModelWrapper), use it
        if hasattr(self.model, "chat") and callable(getattr(self.model, "chat")):
            messages = self.memory.get_messages()
            res = self.model.chat(messages)
            return res.get("message", {}).get("content", "")

        # Standard HuggingFace model generation
        raw_inputs = self.tokenizer(prompt, return_tensors="pt", truncation=True, max_length=2048)
        if hasattr(raw_inputs, "to"):
            inputs = raw_inputs.to(self.device)
        elif isinstance(raw_inputs, dict):
            inputs = {k: (v.to(self.device) if hasattr(v, "to") else v) for k, v in raw_inputs.items()}
        else:
            inputs = raw_inputs

        pad_token_id = getattr(self.tokenizer, "pad_token_id", None) or getattr(self.tokenizer, "eos_token_id", None)

        with torch.no_grad():
            outputs = self.model.generate(
                **inputs,
                max_new_tokens=max_new_tokens,
                do_sample=True,
                temperature=0.7,
                top_p=0.9,
                pad_token_id=pad_token_id,
            )

        # Extract input length for slicing generated output
        if hasattr(inputs, "input_ids"):
            input_len = inputs.input_ids.shape[1]
        elif isinstance(inputs, dict) and "input_ids" in inputs:
            input_len = inputs["input_ids"].shape[1]
        else:
            input_len = 0
        generated_ids = outputs[0][input_len:]
        return self.tokenizer.decode(generated_ids, skip_special_tokens=True)


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
