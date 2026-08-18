"""Utility functions for weight (de)serialization in federated learning."""
import logging
from collections import OrderedDict

import numpy as np
import torch
import torch.nn as nn

logger = logging.getLogger(__name__)

def _is_peft_model(model: nn.Module) -> bool:
    """Check if model has attached PEFT LoRA adapters."""
    return hasattr(model, "peft_config") or hasattr(model, "active_adapter")

def get_parameters(model: nn.Module) -> list[np.ndarray]:
    """
    Extract model parameters as a list of numpy arrays.
    For PEFT/LoRA models, extracts ONLY trainable adapter parameters.
    """
    if _is_peft_model(model):
        try:
            from peft import get_peft_model_state_dict
            state_dict = get_peft_model_state_dict(model)
            return [val.cpu().detach().numpy().copy() for _, val in state_dict.items()]
        except ImportError:
            logger.warning("PEFT model detected but peft library not available; using full state_dict")

    return [val.cpu().detach().numpy().copy() for _, val in model.state_dict().items()]

def set_parameters(model: nn.Module, parameters: list[np.ndarray]) -> None:
    """
    Load a list of numpy arrays into model parameters.
    For PEFT/LoRA models, updates ONLY trainable adapter parameters.
    """
    if _is_peft_model(model):
        try:
            from peft import get_peft_model_state_dict, set_peft_model_state_dict
            state_dict = get_peft_model_state_dict(model)
            params_dict = zip(state_dict.keys(), parameters)
            new_state_dict = OrderedDict({k: torch.tensor(v) for k, v in params_dict})
            set_peft_model_state_dict(model, new_state_dict)
            return
        except ImportError:
            logger.warning("PEFT model detected but peft library not available; using full load_state_dict")

    params_dict = zip(model.state_dict().keys(), parameters)
    state_dict = OrderedDict({k: torch.tensor(v) for k, v in params_dict})
    model.load_state_dict(state_dict, strict=True)

def flatten_weights(parameters: list[np.ndarray]) -> np.ndarray:
    """
    Concatenate all parameter arrays into a single 1D float64 vector.
    """
    if not parameters:
        return np.array([], dtype=np.float64)
    return np.concatenate([p.ravel() for p in parameters]).astype(np.float64)

def unflatten_weights(flat: np.ndarray, shapes: list[tuple]) -> list[np.ndarray]:
    """
    Split a 1D vector back into a list of arrays with the given shapes.
    """
    parameters = []
    pointer = 0
    for shape in shapes:
        size = int(np.prod(shape))
        param = flat[pointer : pointer + size].reshape(shape)
        parameters.append(param)
        pointer += size
    return parameters

def get_parameter_shapes(model: nn.Module) -> list[tuple]:
    """
    Return the shapes of all model parameters (or LoRA adapter parameters if PEFT model).
    """
    if _is_peft_model(model):
        try:
            from peft import get_peft_model_state_dict
            state_dict = get_peft_model_state_dict(model)
            return [tuple(val.shape) for _, val in state_dict.items()]
        except ImportError:
            pass
    return [tuple(val.shape) for _, val in model.state_dict().items()]

