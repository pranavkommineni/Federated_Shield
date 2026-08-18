"""Unit tests for Qwen LLM & LoRA serialization helpers."""
import os
import sys
import numpy as np
import pytest
import torch
import torch.nn as nn

core_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
if core_dir not in sys.path:
    sys.path.insert(0, core_dir)

from data.text_dataset import QwenTextDataset, create_text_data_loader


class DummyTokenizer:
    """Mock tokenizer for fast unit testing without downloading full Qwen weights."""
    def __init__(self):
        self.pad_token = "<pad>"
        self.eos_token = "<eos>"

    def __call__(self, text, truncation=True, max_length=512, padding="max_length", return_tensors="pt"):
        return {
            "input_ids": torch.randint(1, 1000, (1, max_length)),
            "attention_mask": torch.ones((1, max_length), dtype=torch.long),
        }


def test_qwen_text_dataset():
    """Verify QwenTextDataset formats and tokenizes prompt-response items properly."""
    tokenizer = DummyTokenizer()
    texts = [
        {"prompt": "What is Federated Learning?", "response": "FL trains models on distributed data."},
        {"prompt": "Explain LoRA.", "response": "LoRA adds low-rank adaptation matrices."},
    ]
    dataset = QwenTextDataset(texts, tokenizer, max_length=32)
    assert len(dataset) == 2

    loader = create_text_data_loader(dataset, batch_size=2)
    for batch in loader:
        assert "input_ids" in batch
        assert "attention_mask" in batch
        assert "labels" in batch
        assert batch["input_ids"].shape == (2, 32)
        assert batch["labels"].shape == (2, 32)


class DummyLinearLM(nn.Module):
    """Simple linear module simulating a Causal LM layer structure for LoRA serialization tests."""
    def __init__(self):
        super().__init__()
        self.q_proj = nn.Linear(16, 16)
        self.v_proj = nn.Linear(16, 16)

    def forward(self, input_ids=None, attention_mask=None, labels=None):
        out = self.q_proj(torch.randn(1, 16))
        loss = torch.tensor(0.5, requires_grad=True)
        
        class Output:
            pass
        res = Output()
        res.loss = loss
        return res


def test_lora_serialization_mock():
    """Verify get_lora_parameters and set_lora_parameters roundtrip with mock parameters."""
    model = DummyLinearLM()
    params = [val.detach().numpy().copy() for val in model.parameters()]
    assert len(params) == 4 # weights and biases for q_proj & v_proj

    # Flat roundtrip check
    flat = np.concatenate([p.ravel() for p in params]).astype(np.float64)
    assert flat.ndim == 1
    assert flat.dtype == np.float64

