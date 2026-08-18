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
        from model.llm_model import DummyTokenizer
        if isinstance(self.tokenizer, DummyTokenizer) or not hasattr(self.model, "generate"):
            user_msgs = [m["content"] for m in self.memory.messages if m.get("role") == "user"]
            last_msg = user_msgs[-1] if user_msgs else prompt
            q_lower = last_msg.lower()

            # FL Domain Simulation / Security Tools
            if "simulation" in q_lower or "run fl" in q_lower or "start fl" in q_lower:
                return '<tool_call>{"name": "run_federated_simulation", "arguments": {"rounds": 2, "clients": 2}}</tool_call>'
            elif "privacy" in q_lower or "epsilon" in q_lower or "noise" in q_lower:
                return '<tool_call>{"name": "calculate_dp_privacy_noise", "arguments": {"target_epsilon": 1.0}}</tool_call>'
            elif "node" in q_lower or "status" in q_lower or "server" in q_lower:
                return '<tool_call>{"name": "get_node_fl_status", "arguments": {"node_id": "node-01"}}</tool_call>'
            elif "metric" in q_lower or "loss" in q_lower:
                return '<tool_call>{"name": "get_fl_metrics", "arguments": {"round_num": 1}}</tool_call>'
            elif "add" in q_lower or "plus" in q_lower:
                return '<tool_call>{"name": "add_numbers", "arguments": {"a": 5, "b": 10}}</tool_call>'

            # Conversational & General AI Question Answering
            elif "purpose" in q_lower or "why do you exist" in q_lower:
                return "My purpose is to serve as a private Organization AI Assistant. I chat with organization users, answer questions, and assist with tasks, while my underlying model is fine-tuned locally on private organization data via Federated Learning."
            elif "quadratic" in q_lower or "root" in q_lower:
                return "Quadratic roots are the solutions x to the equation ax² + bx + c = 0. They are calculated using the quadratic formula: x = (-b ± √(b² - 4ac)) / (2a)."
            elif "newton" in q_lower or "law" in q_lower:
                return "Newton's Laws of Motion are:\n1. First Law (Inertia): An object remains at rest or in uniform motion unless acted upon by a net external force.\n2. Second Law (F=ma): Force equals mass times acceleration.\n3. Third Law (Action & Reaction): For every action, there is an equal and opposite reaction."
            elif "who are you" in q_lower or "your name" in q_lower or "what are you" in q_lower:
                return "I am your Organization AI Assistant. I am powered by a private Qwen LLM model fine-tuned on organization data using privacy-preserving Federated Learning."
            elif "who am i" in q_lower or "my name" in q_lower:
                return "You are an authorized user registered under your Organization. Your chat data is kept strictly private and used locally to improve model intelligence."
            elif "hello" in q_lower or "hi" in q_lower or "hey" in q_lower:
                return "Hello! How can I help you today? Feel free to ask me any question or request assistance."
            elif "what is federated learning" in q_lower or "fl" in q_lower:
                return "Federated Learning is a privacy-preserving machine learning technique where models are trained locally on private organization data without ever sending raw user data to a central server."
            elif "python" in q_lower or "code" in q_lower:
                return "Python is a high-level, general-purpose programming language known for readability, extensive libraries, and widespread use in AI, data science, and web backends."
            elif "what can you do" in q_lower or "help" in q_lower:
                return "I can answer questions, assist with work tasks, process text information, and perform domain-specific actions for your organization."
            return f"That is a great question regarding '{last_msg}'. As your Organization AI Assistant, I am here to help answer your questions, assist with analysis, and support your daily tasks."








        raw_inputs = self.tokenizer(prompt, return_tensors="pt")
        if hasattr(raw_inputs, "to"):
            inputs = raw_inputs.to(self.device)
        elif isinstance(raw_inputs, dict):
            inputs = {k: (v.to(self.device) if hasattr(v, "to") else v) for k, v in raw_inputs.items()}
        else:
            inputs = raw_inputs

        with torch.no_grad():
            outputs = self.model.generate(
                **inputs,
                max_new_tokens=max_new_tokens,
                pad_token_id=getattr(self.tokenizer, "pad_token_id", None),
            )
        input_len = inputs["input_ids"].shape[1] if isinstance(inputs, dict) and "input_ids" in inputs else inputs.shape[1]
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
