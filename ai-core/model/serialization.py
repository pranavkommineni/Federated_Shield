"""Utility functions for weight (de)serialization in federated learning."""
import logging
from collections import OrderedDict

import numpy as np
import torch
import torch.nn as nn

logger = logging.getLogger(__name__)

def get_parameters(model: nn.Module) -> list[np.ndarray]:
    """
    Extract model parameters as a list of numpy arrays.
    
    Args:
        model: PyTorch model.
        
    Returns:
        A list of numpy arrays representing the model's parameters.
    """
    return [val.cpu().detach().numpy().copy() for _, val in model.state_dict().items()]

def set_parameters(model: nn.Module, parameters: list[np.ndarray]) -> None:
    """
    Load a list of numpy arrays into model parameters.
    
    Args:
        model: PyTorch model.
        parameters: List of numpy arrays to load into the model.
    """
    params_dict = zip(model.state_dict().keys(), parameters)
    state_dict = OrderedDict({k: torch.tensor(v) for k, v in params_dict})
    model.load_state_dict(state_dict, strict=True)

def flatten_weights(parameters: list[np.ndarray]) -> np.ndarray:
    """
    Concatenate all parameter arrays into a single 1D float64 vector.
    
    Args:
        parameters: List of numpy arrays.
        
    Returns:
        A 1D numpy array of concatenated parameters in float64.
    """
    if not parameters:
        return np.array([], dtype=np.float64)
    return np.concatenate([p.ravel() for p in parameters]).astype(np.float64)

def unflatten_weights(flat: np.ndarray, shapes: list[tuple]) -> list[np.ndarray]:
    """
    Split a 1D vector back into a list of arrays with the given shapes.
    
    Args:
        flat: 1D numpy array containing all parameters.
        shapes: List of tuples specifying the shape of each original array.
        
    Returns:
        List of numpy arrays with the specified shapes.
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
    Return the shapes of all model parameters.
    
    Args:
        model: PyTorch model.
        
    Returns:
        List of tuples representing the shapes of the model's parameters.
    """
    return [tuple(val.shape) for _, val in model.state_dict().items()]
