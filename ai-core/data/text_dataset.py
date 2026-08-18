"""Scholar Q&A and text dataset tokenization loader for Qwen LLM fine-tuning."""
import torch
from torch.utils.data import Dataset, DataLoader

class QwenTextDataset(Dataset):
    """
    Dataset wrapper for formatting & tokenizing prompt-response texts for Causal LM training.
    """
    def __init__(self, texts: list[dict[str, str]], tokenizer, max_length: int = 512):
        """
        Args:
            texts: List of dicts with keys 'prompt' and 'response' or 'text'.
            tokenizer: Pretrained Qwen tokenizer.
            max_length: Maximum sequence token length.
        """
        self.examples = []
        for item in texts:
            if "prompt" in item and "response" in item:
                formatted_text = f"<|im_start|>user\n{item['prompt']}<|im_end|>\n<|im_start|>assistant\n{item['response']}<|im_end|>"
            else:
                formatted_text = item.get("text", "")

            encodings = tokenizer(
                formatted_text,
                truncation=True,
                max_length=max_length,
                padding="max_length",
                return_tensors="pt",
            )
            
            input_ids = encodings["input_ids"].squeeze(0)
            attention_mask = encodings["attention_mask"].squeeze(0)
            
            # For Causal LM, labels equal input_ids (with padding masked as -100)
            labels = input_ids.clone()
            labels[attention_mask == 0] = -100

            self.examples.append({
                "input_ids": input_ids,
                "attention_mask": attention_mask,
                "labels": labels,
            })

    def __len__(self) -> int:
        return len(self.examples)

    def __getitem__(self, idx: int) -> dict[str, torch.Tensor]:
        return self.examples[idx]


def create_text_data_loader(
    dataset: QwenTextDataset,
    batch_size: int = 2,
    shuffle: bool = True,
) -> DataLoader:
    """Create PyTorch DataLoader for LLM text datasets."""
    return DataLoader(dataset, batch_size=batch_size, shuffle=shuffle)
