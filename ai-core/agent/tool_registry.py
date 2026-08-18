"""Tool Registry for registering Python functions and generating JSON tool schemas."""
import inspect
import json
import logging
from typing import Callable, Any, Dict, List

logger = logging.getLogger(__name__)


def _python_type_to_json_type(py_type: Any) -> str:
    """Map python types to JSON schema types."""
    if py_type in (int, float):
        return "number" if py_type is float else "integer"
    elif py_type is bool:
        return "boolean"
    elif py_type in (list, tuple):
        return "array"
    elif py_type is dict:
        return "object"
    return "string"


class ToolRegistry:
    """Registry for managing executable tools and generating JSON schemas."""

    def __init__(self):
        self._tools: Dict[str, Callable] = {}
        self._schemas: Dict[str, Dict[str, Any]] = {}

    def register(self, func: Callable = None, name: str = None, description: str = None):
        """Decorator or direct method to register a Python function as an agent tool."""
        def decorator(f: Callable):
            tool_name = name or f.__name__
            tool_doc = description or (f.__doc__ or "").strip()
            
            sig = inspect.signature(f)
            properties = {}
            required = []

            for param_name, param in sig.parameters.items():
                if param_name in ("self", "cls"):
                    continue
                param_type = param.annotation if param.annotation != inspect.Parameter.empty else str
                properties[param_name] = {
                    "type": _python_type_to_json_type(param_type),
                    "description": f"Parameter {param_name}",
                }
                if param.default == inspect.Parameter.empty:
                    required.append(param_name)

            schema = {
                "type": "function",
                "function": {
                    "name": tool_name,
                    "description": tool_doc,
                    "parameters": {
                        "type": "object",
                        "properties": properties,
                        "required": required,
                    },
                },
            }

            self._tools[tool_name] = f
            self._schemas[tool_name] = schema
            logger.info(f"Registered tool '{tool_name}'")
            return f

        if func is not None:
            return decorator(func)
        return decorator

    def get_tools_schema(self) -> List[Dict[str, Any]]:
        """Get list of JSON tool schemas formatted for ChatML / HF apply_chat_template."""
        return list(self._schemas.values())

    def execute_tool(self, tool_name: str, arguments: Dict[str, Any]) -> str:
        """Execute a registered tool by name with arguments and return result string."""
        if tool_name not in self._tools:
            return f"Error: Tool '{tool_name}' not found in registry."

        try:
            if isinstance(arguments, str):
                arguments = json.loads(arguments)
            func = self._tools[tool_name]
            result = func(**arguments)
            if isinstance(result, (dict, list)):
                return json.dumps(result)
            return str(result)
        except Exception as e:
            logger.error(f"Error executing tool '{tool_name}': {e}")
            return f"Error executing tool '{tool_name}': {str(e)}"
