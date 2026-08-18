"""Local Causal LM fine-tuning utilities for Qwen LLM with LoRA."""
import logging
import torch
import torch.nn as nn
from torch.utils.data import DataLoader

logger = logging.getLogger(__name__)

def train_local_llm(
    peft_model: nn.Module,
    train_loader: DataLoader,
    epochs: int = 1,
    learning_rate: float = 2e-4,
    device: torch.device | None = None,
) -> tuple[float, int]:
    """
    Train local PEFT/LoRA LLM over tokenized text data batches.

    Args:
        peft_model: PyTorch model with LoRA attached.
        train_loader: DataLoader containing input_ids, attention_mask, labels.
        epochs: Number of local training epochs.
        learning_rate: AdamW learning rate (typically 1e-4 to 3e-4 for LoRA).
        device: Computing device.

    Returns:
        Tuple of (average_loss, total_samples).
    """
    if device is None:
        device = torch.device("cuda" if torch.cuda.is_available() else "cpu")

    peft_model.to(device)
    peft_model.train()

    optimizer = torch.optim.AdamW(peft_model.parameters(), lr=learning_rate)
    total_samples = 0
    last_epoch_loss = 0.0

    for epoch in range(epochs):
        epoch_loss = 0.0
        epoch_samples = 0

        for batch in train_loader:
            input_ids = batch["input_ids"].to(device)
            attention_mask = batch["attention_mask"].to(device)
            labels = batch["labels"].to(device)

            optimizer.zero_grad()
            outputs = peft_model(
                input_ids=input_ids,
                attention_mask=attention_mask,
                labels=labels,
            )
            loss = outputs.loss
            loss.backward()
            optimizer.step()

            batch_size = len(input_ids)
            epoch_samples += batch_size
            epoch_loss += loss.item() * batch_size

        last_epoch_loss = epoch_loss / epoch_samples if epoch_samples > 0 else 0.0
        total_samples = epoch_samples

    return last_epoch_loss, total_samples
