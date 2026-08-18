"""
Interactive CLI & Demo Script for Federated Shield Autonomous Agent
Demonstrates live model chat with dynamic tool execution using Ollama (qwen2.5:3b).
"""

import sys
import os
import logging

# Ensure ai-core module is on path
base_dir = os.path.dirname(os.path.abspath(__file__))
ai_core_dir = os.path.join(base_dir, "ai-core")
if ai_core_dir not in sys.path:
    sys.path.insert(0, ai_core_dir)

from agent.ollama_agent import OllamaAgent
from agent.tool_registry import ToolRegistry
from model.ollama_model import is_ollama_available

# Suppress debug noise for clean UI
logging.basicConfig(level=logging.WARNING)


def create_demo_registry() -> ToolRegistry:
    """Create a registry equipped with sample domain tools."""
    registry = ToolRegistry()

    @registry.register(name="get_server_status", description="Get operational status of a federated node or server")
    def get_server_status(server_id: str) -> str:
        statuses = {
            "node-01": "ONLINE - CPU 24%, Memory 3.2GB, Active FL Round: #3",
            "node-02": "ONLINE - CPU 18%, Memory 2.8GB, Active FL Round: #3",
            "server-main": "ONLINE - Aggregator healthy, Secure Aggregation enabled",
        }
        return statuses.get(server_id.lower(), f"Server '{server_id}' is ONLINE (default node status).")

    @registry.register(name="get_fl_metrics", description="Fetch federated learning training metrics for a round")
    def get_fl_metrics(round_num: int) -> dict:
        metrics = {
            1: {"loss": 1.45, "accuracy": "62.4%", "epsilon": 0.5},
            2: {"loss": 0.82, "accuracy": "78.1%", "epsilon": 1.0},
            3: {"loss": 0.41, "accuracy": "89.5%", "epsilon": 1.5},
        }
        return metrics.get(round_num, {"loss": 0.35, "accuracy": "91.2%", "epsilon": 2.0})

    @registry.register(name="calculate_privacy_budget", description="Calculate Differential Privacy epsilon bound")
    def calculate_privacy_budget(noise_multiplier: float, steps: int) -> str:
        eps = round(noise_multiplier * (steps ** 0.5) * 0.1, 4)
        return f"Differential Privacy bound: Epsilon = {eps}, Delta = 1e-5 (Strict Privacy Guaranteed)"

    @registry.register(name="add_numbers", description="Add two numbers together")
    def add_numbers(a: float, b: float) -> str:
        return str(a + b)

    return registry


def run_demo_queries(agent: OllamaAgent):
    """Run a pre-scripted demo showing tool call turn-by-turn."""
    print("=" * 65)
    print(" 🛡️  FEDERATED SHIELD AGENT DEMO (Live Ollama qwen2.5:3b) 🛡️")
    print("=" * 65)
    print()

    demo_queries = [
        "Hello! Who are you and what can you help me with?",
        "Can you check the status of federated training node 'node-01'?",
        "What were the federated training metrics for round 3?",
        "Calculate the privacy budget with noise_multiplier=1.5 and steps=100.",
    ]

    for idx, query in enumerate(demo_queries, 1):
        print(f"\n[Demo Turn {idx}] User: {query}")
        print("-" * 50)
        try:
            response = agent.run(query, max_turns=3)
            print(f"Agent Response:\n{response}")
        except Exception as e:
            print(f"Error during execution: {e}")
        print("=" * 65)


def interactive_chat(agent: OllamaAgent):
    """Interactive loop for chatting with the agent."""
    print("\n" + "=" * 65)
    print(" 💬 INTERACTIVE AGENT CHAT MODE")
    print(" Type 'exit' or 'quit' to end the session.")
    print("=" * 65 + "\n")

    while True:
        try:
            user_input = input("\nYou > ").strip()
            if not user_input:
                continue
            if user_input.lower() in ("exit", "quit", "q"):
                print("Ending chat demo session. Goodbye!")
                break

            response = agent.run(user_input, max_turns=5)
            print(f"\nAgent > {response}")
        except (KeyboardInterrupt, EOFError):
            print("\nExiting chat mode...")
            break


def main():
    if not is_ollama_available():
        print("❌ Ollama server is not running on http://localhost:11434.")
        print("Please start Ollama service first: `ollama serve`")
        sys.exit(1)

    print("✅ Ollama detected! Initializing Federated Shield Tool Agent...")
    registry = create_demo_registry()
    agent = OllamaAgent(model_name="qwen2.5:3b", tool_registry=registry)

    # First run live demo queries
    run_demo_queries(agent)

    # If interactive arg or tty is active, launch chat mode
    if "--interactive" in sys.argv or sys.stdin.isatty():
        interactive_chat(agent)


if __name__ == "__main__":
    main()
