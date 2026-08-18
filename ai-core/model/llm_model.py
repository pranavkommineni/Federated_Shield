import logging
from collections import OrderedDict
import numpy as np
import torch
import importlib.metadata

_orig_meta_version = importlib.metadata.version

def _safe_meta_version(dist_name: str) -> str:
    if dist_name.lower() in ("torch", "torchvision", "torchaudio"):
        try:
            val = _orig_meta_version(dist_name)
            if val is not None:
                return val
        except Exception:
            pass
        return "2.13.0"
    return _orig_meta_version(dist_name)

importlib.metadata.version = _safe_meta_version

logger = logging.getLogger(__name__)

# Default model target
DEFAULT_QWEN_MODEL = "Qwen/Qwen2.5-3B-Instruct"



def load_qwen_model_and_tokenizer(
    model_name_or_path: str = DEFAULT_QWEN_MODEL,
    load_in_4bit: bool = True,
    device_map: str = "auto",
):
    """
    Waterfall Resolution Strategy:
    1. If Ollama service is present & running locally with target model, return Ollama model wrapper.
    2. Else if direct model files are present locally (local_files_only), load from system cache.
    3. Else try online download from Hugging Face Hub.
    4. Else throw clear error stating LLM is unavailable.
    """
    # 1. Check if Ollama is present locally
    try:
        from model.ollama_model import is_ollama_available, OllamaModelWrapper
        if is_ollama_available(model_name="qwen2.5:3b"):
            logger.info("Waterfall Step 1: Ollama detected locally with 'qwen2.5:3b'. Using local Ollama model.")
            return OllamaModelWrapper(model_name="qwen2.5:3b"), None
    except Exception as e_ollama:
        logger.debug(f"Ollama check skipped: {e_ollama}")

    from transformers import AutoModelForCausalLM, AutoTokenizer

    tokenizer = None

    # 2. Check if direct model present locally
    try:
        tokenizer = AutoTokenizer.from_pretrained(model_name_or_path, local_files_only=True, trust_remote_code=True)
        logger.info(f"Waterfall Step 2: Direct model '{model_name_or_path}' found locally on system.")
    except Exception:
        # 3. Try online download from HF Hub
        try:
            logger.info(f"Waterfall Step 3: Local files not found. Attempting online download for '{model_name_or_path}'...")
            tokenizer = AutoTokenizer.from_pretrained(model_name_or_path, trust_remote_code=True)
        except Exception as e_online:
            # 4. Explicit Error
            raise RuntimeError(
                f"LLM is unavailable: Ollama is not running locally, "
                f"no direct model files for '{model_name_or_path}' were found locally, "
                f"and online download failed ({e_online})."
            ) from e_online

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
        model = AutoModelForCausalLM.from_pretrained(model_name_or_path, local_files_only=True, **model_kwargs)
    except Exception:
        try:
            model = AutoModelForCausalLM.from_pretrained(model_name_or_path, **model_kwargs)
        except Exception as e_final:
            raise RuntimeError(
                f"LLM weights are unavailable: Ollama is not running locally, "
                f"no direct model weights for '{model_name_or_path}' were found locally, "
                f"and online download failed ({e_final})."
            ) from e_final

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

    def generate(self, **kwargs):
        return torch.randint(1, 1000, (1, 32))


class DummyTokenizer:
    """Mock tokenizer for fast testing without downloading model weights."""
    def __init__(self):
        self.pad_token = "<pad>"
        self.eos_token = "<eos>"
        self.pad_token_id = 0
        self.eos_token_id = 1

    def __call__(self, text, truncation=True, max_length=512, padding="max_length", return_tensors="pt"):
        return {
            "input_ids": torch.randint(1, 1000, (1, max_length)),
            "attention_mask": torch.ones((1, max_length), dtype=torch.long),
        }

    def encode(self, text, **kwargs):
        return [1, 2, 3]

    def decode(self, token_ids, **kwargs):
        return "Federated Shield Scholar: Agent tool execution complete."

    def apply_chat_template(self, messages, tokenize=False, add_generation_prompt=True, **kwargs):
        return "\n".join([f"{m.get('role', 'user')}: {m.get('content', '')}" for m in messages])

    def batch_decode(self, sequences, skip_special_tokens=True):
        return ["Federated Shield Scholar: Qwen AI assistant response."]




import threading
_thread_lock = threading.Lock()


class ChatSession:
    """
    Thread-safe Chat Session managing message history and model generation for Qwen LLMs and Ollama models.
    """
    def __init__(
        self,
        model,
        tokenizer=None,
        system_prompt: str = "You are a helpful academic AI research assistant for scholars.",
        session_id: str | None = None,
    ):
        self.model = model
        self.tokenizer = tokenizer
        self.session_id = session_id or "default"
        self.system_prompt = system_prompt
        self.messages: list[dict[str, str]] = []
        self.reset()

    def reset(self, new_system_prompt: str | None = None) -> None:
        """Reset conversation history with optional new system prompt."""
        if new_system_prompt is not None:
            self.system_prompt = new_system_prompt
        self.messages = [{"role": "system", "content": self.system_prompt}]

    def add_user_message(self, content: str) -> None:
        """Append a user message to session history."""
        self.messages.append({"role": "user", "content": content})

    def add_assistant_message(self, content: str) -> None:
        """Append an assistant response to session history."""
        self.messages.append({"role": "assistant", "content": content})

    def generate_reply(
        self,
        user_input: str,
        max_new_tokens: int = 512,
        temperature: float = 0.7,
        top_p: float = 0.9,
    ) -> str:
        """
        Add user input, execute model generation, record assistant response, and return output text.
        """
        self.add_user_message(user_input)

        # Check if Ollama model wrapper
        if hasattr(self.model, "chat") and callable(getattr(self.model, "chat")):
            res = self.model.chat(self.messages)
            msg = res.get("message", {}).get("content", "")
            self.add_assistant_message(msg)
            return msg

        # Otherwise Hugging Face model
        if self.tokenizer is None:
            raise ValueError("Tokenizer must be provided for Hugging Face model chat generation.")

        text = self.tokenizer.apply_chat_template(
            self.messages,
            tokenize=False,
            add_generation_prompt=True,
        )

        try:
            device = next(self.model.parameters()).device
        except (StopIteration, AttributeError):
            device = torch.device("cpu")

        model_inputs = self.tokenizer([text], return_tensors="pt")
        if hasattr(model_inputs, "to"):
            model_inputs = model_inputs.to(device)
        elif isinstance(model_inputs, dict):
            model_inputs = {k: (v.to(device) if hasattr(v, "to") else v) for k, v in model_inputs.items()}

        pad_token_id = getattr(self.tokenizer, "pad_token_id", None) or getattr(self.tokenizer, "eos_token_id", None)

        with _thread_lock:
            with torch.no_grad():
                generated_ids = self.model.generate(
                    **model_inputs,
                    max_new_tokens=max_new_tokens,
                    do_sample=True if temperature > 0 else False,
                    temperature=temperature if temperature > 0 else 1.0,
                    top_p=top_p,
                    pad_token_id=pad_token_id,
                )

        input_ids_tensor = model_inputs.input_ids if hasattr(model_inputs, "input_ids") else model_inputs["input_ids"]
        generated_ids = [
            output_ids[len(in_ids):]
            for in_ids, output_ids in zip(input_ids_tensor, generated_ids)
        ]

        response = self.tokenizer.batch_decode(generated_ids, skip_special_tokens=True)[0]
        self.add_assistant_message(response)
        return response


