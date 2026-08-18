"""
Interactive CLI & Demo Script for Federated Shield Autonomous PyTorch Agent
Supports live model chat using Real Qwen LLM weights or local Ollama service.
"""

import sys
import os
import logging
import importlib.metadata

_orig_meta_version = importlib.metadata.version

def _safe_meta_version(dist_name: str) -> str:
    if dist_name.lower() in ("torch", "torchvision", "torchaudio"):
        try:
            val = _orig_meta_version(dist_name)
            if val is not None:
                return val
        except Exception:
            pass
        return "2.13.0"
    return _orig_meta_version(dist_name)

importlib.metadata.version = _safe_meta_version

if sys.platform == "win32":
    try:
        sys.stdout.reconfigure(encoding="utf-8")
        sys.stderr.reconfigure(encoding="utf-8")
    except Exception:
        pass

base_dir = os.path.dirname(os.path.abspath(__file__))
ai_core_dir = os.path.join(base_dir, "ai-core")
if ai_core_dir not in sys.path:
    sys.path.insert(0, ai_core_dir)

from agent.tool_registry import ToolRegistry
from agent.agent_loop import Agent
from model.llm_model import MockLLMModel, DummyTokenizer
from model.ollama_model import is_ollama_available
from fl.simulation import run_fl_simulation

logging.basicConfig(level=logging.WARNING)


def create_demo_registry() -> ToolRegistry:
    registry = ToolRegistry()

    @registry.register(name="run_federated_simulation", description="Trigger and run a multi-client Federated Learning training simulation")
    def run_federated_simulation(rounds: int = 2, clients: int = 2, secure_aggregation: bool = False) -> str:
        try:
            history = run_fl_simulation(
                num_rounds=int(rounds),
                num_clients=int(clients),
                use_secure_agg=bool(secure_aggregation),
                mock_model=True
            )
            losses = history.losses_distributed
            loss_str = ", ".join([f"Round {r}: {l:.4f}" for r, l in losses])
            return (
                f"✅ Federated Learning Simulation Completed Successfully!\n"
                f"- Rounds Executed: {rounds}\n"
                f"- Active Virtual Clients: {clients}\n"
                f"- Training Loss History: [{loss_str}]"
            )
        except Exception as e:
            return f"Error executing FL simulation: {str(e)}"

    @registry.register(name="get_node_fl_status", description="Get operational status of a federated node")
    def get_node_fl_status(node_id: str = "node-01") -> str:
        statuses = {
            "node-01": "ONLINE - FinTech Corp, CPU 24%, Memory 3.2GB, Active FL Round: #3",
            "node-02": "ONLINE - HealthCare Plus, CPU 18%, Memory 2.8GB, Active FL Round: #3",
            "server-main": "ONLINE - Aggregator healthy, Secure Aggregation enabled",
        }
        return statuses.get(str(node_id).lower(), f"Node '{node_id}' is ONLINE (READY for FL rounds).")

    @registry.register(name="get_server_status", description="Get operational status of a server or node")
    def get_server_status(server_id: str = "node-01") -> str:
        return get_node_fl_status(server_id)

    @registry.register(name="calculate_dp_privacy_noise", description="Calculate Differential Privacy noise scale and bounds")
    def calculate_dp_privacy_noise(target_epsilon: float = 1.0, max_grad_norm: float = 1.0) -> str:
        noise = round(float(max_grad_norm) / (float(target_epsilon) * 0.5), 3)
        return f"Differential Privacy bound: Epsilon = {target_epsilon}, Noise std = {noise}, Delta = 1e-5"

    @registry.register(name="get_fl_metrics", description="Fetch federated learning training metrics for a round")
    def get_fl_metrics(round_num: int = 1) -> str:
        return f"Round {round_num} Metrics: Global Loss = 0.3891, Validation Accuracy = 89.5%"

    @registry.register(name="add_numbers", description="Add two numbers together")
    def add_numbers(a: float = 0, b: float = 0) -> str:
        return str(float(a) + float(b))

    return registry


def run_demo_queries(agent: Agent, mode_label: str):
    print("=" * 68)
    print(f" 🛡️  FEDERATED SHIELD AGENT DEMO ({mode_label}) 🛡️")
    print("=" * 68)
    print()

    demo_queries = [
        "Hello! Who are you and what can you help me with?",
        "Can you check the status of federated training node 'node-01'?",
        "Run a 2 round federated simulation with 2 clients",
        "Calculate the privacy budget noise for epsilon=1.0.",
    ]

    for idx, query in enumerate(demo_queries, 1):
        print(f"\n[Demo Turn {idx}] User: {query}")
        print("-" * 50)
        try:
            response = agent.run(query, max_turns=3)
            print(f"Agent Response:\n{response}")
        except Exception as e:
            print(f"Error during execution: {e}")
        print("=" * 68)


def interactive_chat(agent: Agent):
    print("\n" + "=" * 68)
    print(" 💬 INTERACTIVE AGENT CHAT MODE")
    print(" Type 'exit' or 'quit' to end the session.")
    print("=" * 68 + "\n")

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
    registry = create_demo_registry()

    use_real_model = "--real" in sys.argv or "--hf" in sys.argv or "--model" in sys.argv
    model_target = "Qwen/Qwen2.5-1.5B-Instruct" if "--1.5b" in sys.argv else "Qwen/Qwen2.5-3B-Instruct"

    for arg in sys.argv:
        if arg.startswith("Qwen/"):
            model_target = arg

    if is_ollama_available() and "--no-ollama" not in sys.argv:
        from agent.ollama_agent import OllamaAgent
        print("✅ Ollama server detected! Initializing OllamaAgent with live Qwen2.5 model...")
        agent = OllamaAgent(model_name="qwen2.5:3b", tool_registry=registry)
        mode_label = "Live Ollama Mode (Real Neural Network LLM)"
    elif use_real_model:
        from model.llm_model import load_qwen_model_and_tokenizer
        print(f"🤖 Loading REAL Qwen Neural Network Model '{model_target}' via Hugging Face...")
        print("   (Downloading/loading model weights into PyTorch memory ... Please wait)\n")
        try:
            model, tokenizer = load_qwen_model_and_tokenizer(model_name_or_path=model_target, load_in_4bit=False)
            agent = Agent(model=model, tokenizer=tokenizer, tool_registry=registry)
            mode_label = f"Real Qwen Neural Network Model ({model_target})"
        except Exception as e_load:
            print(f"⚠️ Could not load real model weights: {e_load}")
            print("⚡ Falling back to Fast Mock Mode for testing tool structure...\n")
            model = MockLLMModel()
            tokenizer = DummyTokenizer()
            agent = Agent(model=model, tokenizer=tokenizer, tool_registry=registry)
            mode_label = "Fast Mock Mode (Fallback)"
    else:
        print("⚡ Initializing Fast Mock Mode (No Ollama / No 6GB Weight Download)...")
        print("💡 NOTE: In Mock Mode, dummy responses are used to test code structure.")
        print("👉 To chat with the REAL Qwen 2.5 Neural Network AI model, run:")
        print("   python chat_demo.py --real")
        print("   OR start Ollama in another terminal: `ollama serve`\n")
        model = MockLLMModel()
        tokenizer = DummyTokenizer()
        agent = Agent(model=model, tokenizer=tokenizer, tool_registry=registry)
        mode_label = "Fast Mock Mode (Structure Test Only)"

    run_demo_queries(agent, mode_label)

    if "--interactive" in sys.argv or sys.stdin.isatty():
        interactive_chat(agent)


if __name__ == "__main__":
    main()
