# Team A — AI Core Module

This module contains model definitions, dataset loading and partitioning, local training and evaluation loops, deployable organization training nodes, and Flower federated learning orchestration strategies.

## Module Structure

```
team-a-ai-core/
├── model/
│   ├── federix_model.py     # PyTorch model architecture (FederixNet)
│   ├── model_config.py      # FL hyperparameter configuration (FLConfig)
│   └── serialization.py     # Parameter (de)serialization & flattening
├── data/
│   ├── dataset.py           # CIFAR-10 data loading and loaders
│   ├── partition.py         # IID partitioning utilities
│   └── non_iid.py           # Dirichlet non-IID partitioning
├── training/
│   ├── train.py             # Local training loop functions
│   ├── evaluate.py          # Local and global evaluation functions
│   └── metrics.py           # Classification metrics computation
├── training_node/
│   └── node.py              # Deployable training node entrypoint
├── fl/
│   ├── client.py            # Flower NumPyClient implementation
│   ├── server.py            # Flower server entrypoint & strategy builder
│   └── strategy.py          # Custom strategies (FederixStrategy, SecureFederixStrategy)
├── tests/                   # AI Core unit and integration test suite
├── requirements.txt         # Module dependencies
└── README.md
```

## Quick Start

### Start FL Server
```python
from team_a_ai_core.fl.server import start_fl_server
from team_a_ai_core.model.model_config import FLConfig

config = FLConfig(server_address="0.0.0.0:8080", num_rounds=5)
start_fl_server(config)
```

### Start Training Node
```python
from team_a_ai_core.training_node.node import TrainingNode

node = TrainingNode(node_id="org-1", server_address="127.0.0.1:8080")
node.start(train_loader, test_loader)
```
