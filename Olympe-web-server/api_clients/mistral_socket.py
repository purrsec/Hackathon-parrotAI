"""Mistral API client configuration and utilities using requests."""

import os
import json
from typing import Any, Dict, List, Optional
from dotenv import load_dotenv
from urllib.request import Request, urlopen
from urllib.error import HTTPError, URLError

# Load environment variables from .env file
load_dotenv()


class _DotDict(dict):
    """
    Minimal helper to access dict keys as attributes.
    Recursively wraps nested dicts and lists for attribute-style access.
    """
    def __getattr__(self, item: str) -> Any:
        value = self.get(item)
        if isinstance(value, dict):
            return _DotDict(value)
        if isinstance(value, list):
            return [_DotDict(v) if isinstance(v, dict) else v for v in value]
        return value

    __setattr__ = dict.__setitem__  # type: ignore
    __delattr__ = dict.__delitem__  # type: ignore


class MistralSocket:
    """Singleton for Mistral API client using requests."""
    
    _instance = None
    _base_url: str = ""
    _headers: Dict[str, str] = {}
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance
    
    def __init__(self):
        """Initialize requests session for Mistral API."""
        if not self._headers:
            self._setup_client()
    
    def _setup_client(self):
        """Setup the requests session with auth headers."""
        api_key = os.getenv("MISTRAL_API_KEY")
        if not api_key:
            raise RuntimeError("MISTRAL_API_KEY is not set")
        
        self._base_url = os.getenv("MISTRAL_BASE_URL", "https://api.mistral.ai/v1")
        self._headers = {
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json",
        }
    
    def _post(self, path: str, payload: Dict[str, Any]) -> Dict[str, Any]:
        """Internal POST helper."""
        if not self._headers:
            self._setup_client()
        
        url = f"{self._base_url.rstrip('/')}/{path.lstrip('/')}"
        try:
            data_bytes = json.dumps(payload).encode("utf-8")
            req = Request(url, data=data_bytes, headers=self._headers, method="POST")
            with urlopen(req, timeout=60) as resp:
                resp_bytes = resp.read()
                resp_text = resp_bytes.decode("utf-8", errors="replace")
                return json.loads(resp_text)
        except HTTPError as e:
            # Attempt to extract API error body
            body = e.read().decode("utf-8", errors="replace") if hasattr(e, "read") else ""
            try:
                err_json = json.loads(body) if body else {"error": {"message": str(e)}}
            except Exception:
                err_json = {"error": {"message": body or str(e)}}
            raise RuntimeError(f"Mistral API error: {err_json}") from e
        except URLError as e:
            raise RuntimeError(f"Mistral API network error: {e}") from e
    
    def create_completion(self, model: str, messages: List[Dict[str, Any]], **kwargs) -> Any:
        """
        Create a chat completion using Mistral API.
        
        Signature mirrors OpenAI's `chat.completions.create` to ease swapping.
        Supported kwargs mapped to Mistral:
          - temperature: float
          - max_tokens or max_output_tokens: int (both map to `max_tokens`)
          - safe_prompt: bool (optional, Mistral-specific)
        Unsupported kwargs are ignored gracefully (e.g., response_format).
        """
        # Map token limits
        max_tokens = None
        if "max_tokens" in kwargs and isinstance(kwargs["max_tokens"], int):
            max_tokens = kwargs["max_tokens"]
        elif "max_output_tokens" in kwargs and isinstance(kwargs["max_output_tokens"], int):
            max_tokens = kwargs["max_output_tokens"]
        
        payload: Dict[str, Any] = {
            "model": model,
            "messages": messages,
        }
        
        temperature = kwargs.get("temperature", None)
        if isinstance(temperature, (int, float)):
            payload["temperature"] = float(temperature)
        
        if isinstance(max_tokens, int):
            payload["max_tokens"] = max_tokens
        
        # Optional Mistral-specific controls
        if "safe_prompt" in kwargs:
            payload["safe_prompt"] = bool(kwargs["safe_prompt"])
        
        # Send request
        data = self._post("/chat/completions", payload)
        # Wrap response to mimic OpenAI dot access: response.choices[0].message.content
        return _DotDict(data)


def get_mistral_socket() -> MistralSocket:
    """Factory function to get or create the Mistral socket instance."""
    return MistralSocket()


