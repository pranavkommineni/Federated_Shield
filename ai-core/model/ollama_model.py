"""Ollama local model integration for Qwen 2.5 3B inference and tool calling."""
import json
import logging
import urllib.request
import urllib.error
from typing import Dict, Any, List, Optional

logger = logging.getLogger(__name__)

DEFAULT_OLLAMA_HOST = "http://localhost:11434"
DEFAULT_OLLAMA_MODEL = "qwen2.5:3b"


def is_ollama_available(
    host: str = DEFAULT_OLLAMA_HOST,
    model_name: str = DEFAULT_OLLAMA_MODEL,
) -> bool:
    """Check if Ollama server is running locally and contains the target model."""
    try:
        req = urllib.request.Request(f"{host.rstrip('/')}/api/tags", headers={"User-Agent": "FederatedShield/1.0"})
        with urllib.request.urlopen(req, timeout=3) as resp:
            data = json.loads(resp.read().decode("utf-8"))
            models = [m.get("name", "").split(":")[0] for m in data.get("models", [])]
            target_base = model_name.split(":")[0]
            if target_base in models or any(model_name in m.get("name", "") for m in data.get("models", [])):
                logger.info(f"Ollama server active at {host} with model '{model_name}'")
                return True
            logger.warning(f"Ollama running at {host}, but model '{model_name}' not found. Models available: {models}")
            return False
    except Exception as e:
        logger.debug(f"Ollama server check failed on {host}: {e}")
        return False


class OllamaModelWrapper:
    """Wrapper class providing clean interface to local Ollama API."""

    def __init__(
        self,
        model_name: str = DEFAULT_OLLAMA_MODEL,
        host: str = DEFAULT_OLLAMA_HOST,
    ):
        self.model_name = model_name
        self.host = host.rstrip("/")

    def chat(
        self,
        messages: List[Dict[str, Any]],
        tools: Optional[List[Dict[str, Any]]] = None,
        stream: bool = False,
    ) -> Dict[str, Any]:
        """Send chat payload to local Ollama endpoint."""
        url = f"{self.host}/api/chat"
        payload = {
            "model": self.model_name,
            "messages": messages,
            "stream": stream,
        }
        if tools:
            payload["tools"] = tools

        req_data = json.dumps(payload).encode("utf-8")
        req = urllib.request.Request(
            url,
            data=req_data,
            headers={"Content-Type": "application/json"},
        )

        try:
            with urllib.request.urlopen(req, timeout=60) as resp:
                return json.loads(resp.read().decode("utf-8"))
        except urllib.error.HTTPError as e:
            error_body = e.read().decode("utf-8")
            raise RuntimeError(f"Ollama HTTP error {e.code}: {error_body}") from e
        except Exception as e:
            raise RuntimeError(f"Failed to connect to local Ollama service at {self.host}: {e}") from e
