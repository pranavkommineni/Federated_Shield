"""CLI entry point for running virtual multi-organization FL simulation on single GPU."""
import argparse
import logging
import os
import sys

base_dir = os.path.dirname(os.path.abspath(__file__))
for candidate in ['ai-core', 'team-a-ai-core', 'ai_core']:
    p = os.path.join(base_dir, candidate)
    if os.path.isdir(p) and p not in sys.path:
        sys.path.insert(0, p)

from fl.simulation import run_fl_simulation

def main():
    logging.basicConfig(level=logging.INFO, format='%(asctime)s [%(name)s] %(levelname)s: %(message)s')

    parser = argparse.ArgumentParser(description="Federated Shield Multi-Org Simulation")
    parser.add_argument("--rounds", type=int, default=5, help="Number of FL rounds")
    parser.add_argument("--clients", type=int, default=4, help="Number of virtual org clients (1 to 4)")
    parser.add_argument("--secure-agg", action="store_true", help="Enable Secure Aggregation strategy")
    parser.add_argument("--model-type", type=str, default="qwen", choices=["qwen", "cnn"], help="Model type")
    parser.add_argument("--mock", action="store_true", help="Use lightweight mock model for fast dry runs / testing")
    parser.add_argument("--epochs", type=int, default=1, help="Local epochs per round")
    parser.add_argument("--lr", type=float, default=2e-4, help="Learning rate")
    args = parser.parse_args()

    run_fl_simulation(
        num_rounds=args.rounds,
        num_clients=args.clients,
        use_secure_agg=args.secure_agg,
        model_type=args.model_type,
        mock_model=args.mock,
        local_epochs=args.epochs,
        learning_rate=args.lr,
    )

if __name__ == "__main__":
    main()
