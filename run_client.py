"""CLI entry point to start a Flower FL client."""
import argparse
import logging
import os
import sys
import torch
from torch.utils.data import DataLoader, TensorDataset
import flwr as fl

base_dir = os.path.dirname(os.path.abspath(__file__))
for candidate in ['ai-core', 'team-a-ai-core', 'ai_core']:
    p = os.path.join(base_dir, candidate)
    if os.path.isdir(p) and p not in sys.path:
        sys.path.insert(0, p)

from model.model_config import FLConfig
from model.federix_model import create_model
from fl.client import FederixClient

logger = logging.getLogger(__name__)

def main():
    logging.basicConfig(level=logging.INFO, format='%(asctime)s [%(name)s] %(levelname)s: %(message)s')

    parser = argparse.ArgumentParser(description='Federix FL Client')
    parser.add_argument('--cid', type=str, required=True, help='Client ID')
    parser.add_argument('--server', type=str, default='127.0.0.1:8080', help='Server address')
    parser.add_argument('--epochs', type=int, default=1, help='Local training epochs')
    parser.add_argument('--batch-size', type=int, default=32, help='Batch size')
    parser.add_argument('--lr', type=float, default=0.01, help='Learning rate')
    parser.add_argument('--total-clients', type=int, default=3, help='Total number of clients')
    args = parser.parse_args()

    config = FLConfig(
        local_epochs=args.epochs,
        batch_size=args.batch_size,
        learning_rate=args.lr,
    )

    model = create_model()

    dummy_data = TensorDataset(
        torch.randn(100, 3, 32, 32),
        torch.randint(0, 10, (100,))
    )
    train_loader = DataLoader(dummy_data, batch_size=args.batch_size)
    test_loader = DataLoader(dummy_data, batch_size=args.batch_size)

    client = FederixClient(
        cid=args.cid,
        model=model,
        train_loader=train_loader,
        test_loader=test_loader,
        config=config,
    )

    logger.info(f'Starting client {args.cid}, connecting to {args.server}')
    fl.client.start_client(
        server_address=args.server,
        client=client.to_client(),
    )

if __name__ == '__main__':
    main()
