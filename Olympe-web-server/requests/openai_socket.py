"""OpenAI Azure client configuration and utilities."""

import os
from dotenv import load_dotenv
from openai import AzureOpenAI, OpenAI

# Load environment variables from .env file
load_dotenv()


class OpenAISocket:
    """Singleton for OpenAI client management with Azure support."""
    
    _instance = None
    _client = None
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance
    
    def __init__(self):
        """Initialize OpenAI client based on configuration."""
        if self._client is None:
            self._setup_client()
    
    def _setup_client(self):
        """Setup the appropriate OpenAI client (Azure or standard)."""
        use_azure = os.getenv("USE_AZURE_OPENAI", "false").lower() == "true"
        
        if use_azure:
            self._client = AzureOpenAI(
                api_key=os.getenv("AZURE_OPENAI_API_KEY"),
                api_version="2024-02-15-preview",
                azure_endpoint=os.getenv("AZURE_OPENAI_ENDPOINT"),
            )
        else:
            self._client = OpenAI(
                api_key=os.getenv("OPENAI_API_KEY"),
            )
    
    def get_client(self):
        """Get the OpenAI client instance."""
        if self._client is None:
            self._setup_client()
        return self._client
    
    def create_completion(self, model: str, messages: list, **kwargs):
        """Create a chat completion using the configured client."""
        return self.get_client().chat.completions.create(
            model=model,
            messages=messages,
            **kwargs,
        )


def get_openai_socket() -> OpenAISocket:
    """Factory function to get or create the OpenAI socket instance."""
    return OpenAISocket()

