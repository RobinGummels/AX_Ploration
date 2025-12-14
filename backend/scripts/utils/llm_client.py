from openai import OpenAI
from typing import List, Dict, Any, Optional
import json

from ..config import OPENAI_API_KEY, OPENAI_MODEL, OPENAI_EMBEDDING_MODEL


class LLMClient:
    """Client for interacting with OpenAI API."""
    
    _instance: Optional["LLMClient"] = None
    
    def __new__(cls):
        """Singleton pattern to reuse client."""
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._client = None
        return cls._instance
    
    def __init__(self):
        if self._client is None:
            self._client = OpenAI(api_key=OPENAI_API_KEY)
    
    def chat_completion(
        self,
        messages: List[Dict[str, str]],
        model: str = OPENAI_MODEL,
        temperature: float = 0.0,
        response_format: Optional[Dict] = None
    ) -> str:
        """Send a chat completion request and return the response content."""
        kwargs = {
            "model": model,
            "messages": messages,
            "temperature": temperature
        }
        
        if response_format:
            kwargs["response_format"] = response_format
        
        response = self._client.chat.completions.create(**kwargs)
        return response.choices[0].message.content
    
    def chat_completion_json(
        self,
        messages: List[Dict[str, str]],
        model: str = OPENAI_MODEL,
        temperature: float = 0.0
    ) -> Dict[str, Any]:
        """Send a chat completion request and parse JSON response."""
        response = self.chat_completion(
            messages=messages,
            model=model,
            temperature=temperature,
            response_format={"type": "json_object"}
        )
        return json.loads(response)
    
    def create_embedding(self, text: str) -> List[float]:
        """Create an embedding for the given text."""
        response = self._client.embeddings.create(
            model=OPENAI_EMBEDDING_MODEL,
            input=text
        )
        return response.data[0].embedding
    
    def create_embeddings(self, texts: List[str]) -> List[List[float]]:
        """Create embeddings for multiple texts."""
        response = self._client.embeddings.create(
            model=OPENAI_EMBEDDING_MODEL,
            input=texts
        )
        return [item.embedding for item in response.data]


# Global instance for convenience
llm_client = LLMClient()