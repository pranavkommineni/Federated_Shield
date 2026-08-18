"""Evaluation script to measure domain tool-calling accuracy and quality pre- and post-FL."""
import os
import sys
import logging
import argparse
from typing import Dict, Any

core_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
if core_dir not in sys.path:
    sys.path.insert(0, core_dir)

from agent.agent_loop import Agent
from agent.tool_registry import ToolRegistry
from model.llm_model import MockLLMModel, DummyTokenizer, load_qwen_model_and_tokenizer, apply_lora_to_model
from data.domain_datasets import ORG_DOMAINS

logger = logging.getLogger(__name__)


def create_eval_tool_registry() -> ToolRegistry:
    """Create registry containing evaluation tools for all simulated org domains."""
    registry = ToolRegistry()

    @registry.register(name="get_server_status", description="Query status of server")
    def get_server_status(server_id: str) -> str:
        return f"Server {server_id} online, CPU: 12%"

    @registry.register(name="restart_service", description="Restart server service")
    def restart_service(service_name: str) -> str:
        return f"Service {service_name} restarted successfully"

    @registry.register(name="get_lab_results", description="Query patient lab results")
    def get_lab_results(patient_id: str) -> str:
        return f"Patient {patient_id} lab results: Normal"

    @registry.register(name="track_order", description="Track ecommerce order")
    def track_order(order_id: str) -> str:
        return f"Order {order_id} status: IN_TRANSIT"

    @registry.register(name="execute_sql", description="Run database SQL query")
    def execute_sql(query: str) -> str:
        return f"Executed SQL successfully: 42 rows"

    return registry


def evaluate_agent_on_domains(
    model: Any,
    tokenizer: Any,
    mock_model: bool = True,
) -> Dict[str, Any]:
    """
    Evaluate agent performance across domain prompts.
    """
    registry = create_eval_tool_registry()
    agent = Agent(model=model, tokenizer=tokenizer, tool_registry=registry)

    results = {}
    for org_key, domain_info in ORG_DOMAINS.items():
        domain_name = domain_info["name"]
        prompts = domain_info["data"]
        successful_calls = 0

        logger.info(f"Evaluating domain '{domain_name}' ({len(prompts)} prompts)...")
        for item in prompts:
            prompt = item["prompt"]
            agent.memory.clear()
            output = agent.run(prompt, max_turns=2)
            
            tool_calls = agent.parse_tool_calls(output)
            if tool_calls or "tool" in str(agent.memory.get_messages()):
                successful_calls += 1

        acc = (successful_calls / len(prompts)) * 100.0
        results[org_key] = {
            "name": domain_name,
            "total": len(prompts),
            "tool_calls_triggered": successful_calls,
            "accuracy": acc,
        }
        logger.info(f"Domain '{domain_name}': Tool-Call Accuracy = {acc:.1f}%")

    return results


def main():
    logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(name)s] %(levelname)s: %(message)s")

    parser = argparse.ArgumentParser(description="Evaluate Decoupled Agent Tool-Calling")
    parser.add_argument("--mock", action="store_true", default=True, help="Use mock linear model for fast test evaluation")
    args = parser.parse_args()

    if args.mock:
        logger.info("Running evaluation with Mock LLM Model...")
        model = MockLLMModel()
        tokenizer = DummyTokenizer()
    else:
        logger.info("Loading Qwen2.5-3B + LoRA model for evaluation...")
        base_model, tokenizer = load_qwen_model_and_tokenizer(load_in_4bit=True)
        model = apply_lora_to_model(base_model, r=8)

    results = evaluate_agent_on_domains(model, tokenizer, mock_model=args.mock)
    print("\n" + "=" * 50)
    print("      EVALUATION SUMMARY RESULTS")
    print("=" * 50)
    for org_key, res in results.items():
        print(f"[{res['name']}]: {res['tool_calls_triggered']}/{res['total']} tool calls triggered ({res['accuracy']:.1f}%)")
    print("=" * 50)


if __name__ == "__main__":
    main()
