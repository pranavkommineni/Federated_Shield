"""Qwen2.5-3B LLM & QLoRA model initialization and serialization utilities for Federated Learning."""
import logging
from collections import OrderedDict
import numpy as np
import torch

logger = logging.getLogger(__name__)

# Default model target
DEFAULT_QWEN_MODEL = "Qwen/Qwen2.5-3B-Instruct"

def load_qwen_model_and_tokenizer(
    model_name_or_path: str = DEFAULT_QWEN_MODEL,
    load_in_4bit: bool = True,
    device_map: str = "auto",
):
    """
    Load Qwen tokenizer and base causal language model.
    
    Supports offline mode by attempting local system cache loading if network fails,
    raising an explicit RuntimeError if the model is unavailable on the system.
    """
    from transformers import AutoModelForCausalLM, AutoTokenizer
    
    tokenizer = None
    try:
        tokenizer = AutoTokenizer.from_pretrained(model_name_or_path, trust_remote_code=True)
    except Exception as e_online:
        logger.warning(f"Online tokenizer load failed for '{model_name_or_path}'. Attempting local system cache...")
        try:
            tokenizer = AutoTokenizer.from_pretrained(model_name_or_path, local_files_only=True, trust_remote_code=True)
        except Exception as e_offline:
            raise RuntimeError(
                f"Model '{model_name_or_path}' is unavailable on the system. "
                f"Offline loading failed and network connection was unsuccessful. "
                f"Please ensure model weights are cached or provide a valid local path."
            ) from e_offline

    if tokenizer.pad_token is None:
        tokenizer.pad_token = tokenizer.eos_token

    quantization_config = None
    if load_in_4bit and torch.cuda.is_available():
        try:
            from transformers import BitsAndBytesConfig
            quantization_config = BitsAndBytesConfig(
                load_in_4bit=True,
                bnb_4bit_quant_type="nf4",
                bnb_4bit_compute_dtype=torch.float16,
                bnb_4bit_use_double_quant=True,
            )
            logger.info("4-bit NF4 quantization enabled via BitsAndBytesConfig")
        except ImportError:
            logger.warning("bitsandbytes not available, loading unquantized model")

    model_kwargs = {"trust_remote_code": True}
    if quantization_config is not None:
        model_kwargs["quantization_config"] = quantization_config
        model_kwargs["device_map"] = device_map
    else:
        if torch.cuda.is_available():
            model_kwargs["torch_dtype"] = torch.float16
            model_kwargs["device_map"] = device_map
        else:
            model_kwargs["torch_dtype"] = torch.float32

    try:
        model = AutoModelForCausalLM.from_pretrained(model_name_or_path, **model_kwargs)
    except Exception as e_online:
        logger.warning(f"Online model weights load failed for '{model_name_or_path}'. Attempting local system cache...")
        try:
            model = AutoModelForCausalLM.from_pretrained(model_name_or_path, local_files_only=True, **model_kwargs)
        except Exception as e_offline:
            raise RuntimeError(
                f"Model weights for '{model_name_or_path}' are unavailable on the system. "
                f"Offline loading failed and network connection was unsuccessful. "
                f"Please ensure model weights are cached or provide a valid local path."
            ) from e_offline

    return model, tokenizer



def apply_lora_to_model(
    model,
    r: int = 16,
    lora_alpha: int = 32,
    lora_dropout: float = 0.05,
    target_modules: list[str] | None = None,
):
    """
    Attach PEFT LoRA adapters to the base language model.
    """
    from peft import get_peft_model, LoraConfig, TaskType

    if target_modules is None:
        target_modules = ["q_proj", "k_proj", "v_proj", "o_proj"]

    lora_config = LoraConfig(
        task_type=TaskType.CAUSAL_LM,
        r=r,
        lora_alpha=lora_alpha,
        lora_dropout=lora_dropout,
        target_modules=target_modules,
        bias="none",
    )

    peft_model = get_peft_model(model, lora_config)
    trainable_params, all_param = peft_model.get_nb_trainable_parameters()
    logger.info(
        f"LoRA Attached: Trainable params: {trainable_params:,} / {all_param:,} "
        f"({100 * trainable_params / all_param:.2f}%)"
    )
    return peft_model


def get_lora_parameters(peft_model) -> list[np.ndarray]:
    """
    Extract ONLY trainable LoRA adapter weights as a list of NumPy arrays for FL transfer.
    """
    from peft import get_peft_model_state_dict

    state_dict = get_peft_model_state_dict(peft_model)
    return [val.cpu().detach().numpy().copy() for _, val in state_dict.items()]


def set_lora_parameters(peft_model, parameters: list[np.ndarray]) -> None:
    """
    Load received LoRA NumPy parameters back into the PEFT model.
    """
    from peft import get_peft_model_state_dict, set_peft_model_state_dict

    state_dict = get_peft_model_state_dict(peft_model)
    params_dict = zip(state_dict.keys(), parameters)
    new_state_dict = OrderedDict({k: torch.tensor(v) for k, v in params_dict})
    set_peft_model_state_dict(peft_model, new_state_dict)


class MockLLMModel(torch.nn.Module):
    """Fast linear mock model simulating Causal LM behavior for unit tests & simulation."""
    def __init__(self):
        super().__init__()
        self.q_proj = torch.nn.Linear(16, 16)
        self.v_proj = torch.nn.Linear(16, 16)

    def forward(self, input_ids=None, attention_mask=None, labels=None):
        dummy_input = torch.randn(1, 16)
        out = self.q_proj(dummy_input) + self.v_proj(dummy_input)
        loss = out.sum() * 0.0 + torch.tensor(0.5, requires_grad=True)

        class Output:
            pass
        res = Output()
        res.loss = loss
        return res


class DummyTokenizer:
    """Mock tokenizer for fast testing without downloading model weights."""
    def __init__(self):
        self.pad_token = "<pad>"
        self.eos_token = "<eos>"

    def __call__(self, text, truncation=True, max_length=512, padding="max_length", return_tensors="pt"):
        return {
            "input_ids": torch.randint(1, 1000, (1, max_length)),
            "attention_mask": torch.ones((1, max_length), dtype=torch.long),
        }

