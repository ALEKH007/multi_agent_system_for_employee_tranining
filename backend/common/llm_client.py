import os
import httpx
import logging
from typing import Dict, Any, List, Optional
from common.security import get_secret

logger = logging.getLogger(__name__)

class OpenRouterClient:
    """Client for OpenRouter LLM Gateway."""
    
    BASE_URL = "https://openrouter.ai/api/v1/chat/completions"
    
    def __init__(self):
        # We load API key dynamically via security helper to avoid hardcoding
        self.api_key = get_secret('OPENROUTER_API_KEY')
        self.default_model = os.environ.get('OPENROUTER_DEFAULT_MODEL', 'meta-llama/llama-3.1-8b-instruct:free')
        self.fallback_model = os.environ.get('OPENROUTER_FALLBACK_MODEL', 'mistralai/mistral-7b-instruct:free')
        
        self.headers = {
            "Authorization": f"Bearer {self.api_key}",
            "HTTP-Referer": "http://localhost:8000",  # Required by OpenRouter
            "X-Title": "Employee Training Multi-Agent System"
        }

    async def generate_chat_completion_async(self, messages: List[Dict[str, str]], model: Optional[str] = None) -> Dict[str, Any]:
        """Async chat completion request with fallback logic."""
        target_model = model or self.default_model
        
        payload = {
            "model": target_model,
            "messages": messages
        }
        
        try:
            async with httpx.AsyncClient() as client:
                response = await client.post(
                    self.BASE_URL,
                    headers=self.headers,
                    json=payload,
                    timeout=30.0
                )
                
                # Check for rate limiting or server errors
                if response.status_code in (429, 500, 502, 503, 504) and target_model != self.fallback_model:
                    logger.warning(f"OpenRouter {response.status_code} on {target_model}. Falling back to {self.fallback_model}.")
                    return await self.generate_chat_completion_async(messages, model=self.fallback_model)
                
                response.raise_for_status()
                return response.json()
                
        except httpx.HTTPError as e:
            logger.error(f"OpenRouter HTTP Error: {str(e)}")
            raise e
        except Exception as e:
            logger.error(f"Unexpected error in LLM client: {str(e)}")
            raise e
            
    def generate_chat_completion_sync(self, messages: List[Dict[str, str]], model: Optional[str] = None) -> Dict[str, Any]:
        """Sync version for CrewAI compatibility."""
        target_model = model or self.default_model
        
        payload = {
            "model": target_model,
            "messages": messages
        }
        
        try:
            with httpx.Client() as client:
                response = client.post(
                    self.BASE_URL,
                    headers=self.headers,
                    json=payload,
                    timeout=30.0
                )
                
                if response.status_code in (429, 500, 502, 503, 504) and target_model != self.fallback_model:
                    logger.warning(f"OpenRouter {response.status_code} on {target_model}. Falling back to {self.fallback_model}.")
                    return self.generate_chat_completion_sync(messages, model=self.fallback_model)
                
                response.raise_for_status()
                return response.json()
                
        except httpx.HTTPError as e:
            logger.error(f"OpenRouter HTTP Error: {str(e)}")
            raise e
        except Exception as e:
            logger.error(f"Unexpected error in LLM client: {str(e)}")
            raise e
