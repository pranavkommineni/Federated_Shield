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
    
    Supports 4-bit NF4 quantization via bitsandbytes for 8 GB RAM compatibility.
    """
    from transformers import AutoModelForCausalLM, AutoTokenizer
    
    tokenizer = AutoTokenizer.from_pretrained(model_name_or_path, trust_remote_code=True)
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

    model = AutoModelForCausalLM.from_pretrained(model_name_or_path, **model_kwargs)
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
