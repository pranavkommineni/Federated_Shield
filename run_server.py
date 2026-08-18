"""CLI entry point to start the Flower FL server."""
import argparse
import logging
import os
import sys

base_dir = os.path.dirname(os.path.abspath(__file__))
for candidate in ['ai-core', 'team-a-ai-core', 'ai_core']:
    p = os.path.join(base_dir, candidate)
    if os.path.isdir(p) and p not in sys.path:
        sys.path.insert(0, p)

from model.model_config import FLConfig
from fl.server import start_fl_server

def main():
    logging.basicConfig(level=logging.INFO, format='%(asctime)s [%(name)s] %(levelname)s: %(message)s')

    parser = argparse.ArgumentParser(description='Federix FL Server')
    parser.add_argument('--address', type=str, default='0.0.0.0:8080', help='Server address')
    parser.add_argument('--rounds', type=int, default=5, help='Number of FL rounds')
    parser.add_argument('--min-clients', type=int, default=2, help='Minimum fit clients')
    parser.add_argument('--min-available', type=int, default=2, help='Minimum available clients')
    parser.add_argument('--fraction-fit', type=float, default=1.0, help='Fraction of clients for fit')
    args = parser.parse_args()

    config = FLConfig(
        server_address=args.address,
        num_rounds=args.rounds,
        min_fit_clients=args.min_clients,
        min_available_clients=args.min_available,
        fraction_fit=args.fraction_fit,
    )

    start_fl_server(config)

if __name__ == '__main__':
    main()
