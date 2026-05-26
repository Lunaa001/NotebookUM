"""Service for AI-powered text summarization using UM Gemma4 API"""

import requests
from typing import Optional
import os
import logging

logger = logging.getLogger(__name__)


class AIService:
    """Service for calling UM Gemma4 API for summarization (CPU-optimized, no circuit breaker)"""
    
    # UM AI Cloud configuration
    API_BASE_URL = "https://ai.cloud.um.edu.ar/api/v1"
    MODEL = "gemma4-26b-16g"
    HEALTH_CHECK_TIMEOUT = 5  # seconds - quick ping to verify connectivity
    API_TIMEOUT = 30  # seconds - full request timeout
    
    def __init__(self, api_key: Optional[str] = None):
        """
        Initialize AI Service with API key.
        
        Health checks are performed per-request instead of using circuit breaker pattern.
        This is simpler, no external dependencies needed.
        
        Args:
            api_key: UM AI API key (or from env variable GEMMA4_API_KEY)
        """
        self.api_key = api_key or os.getenv("GEMMA4_API_KEY")
    
    def _check_api_health(self) -> bool:
        """
        Check if API is reachable with a quick ping.
        
        Returns:
            True if API responds, False if unreachable (no error thrown)
        """
        try:
            response = requests.get(
                f"{self.API_BASE_URL}/health",
                headers={"Authorization": f"Bearer {self.api_key}"},
                timeout=self.HEALTH_CHECK_TIMEOUT
            )
            return response.status_code in [200, 204]
        except (requests.Timeout, requests.ConnectionError):
            logger.warning(f"API health check timeout or connection error")
            return False
        except Exception as e:
            logger.warning(f"API health check failed: {str(e)}")
            return False
    
    def generate_summary(self, text: str, max_tokens: int = 200) -> str:
        """
        Generate a summary of the provided text using Gemma4.
        
        Health check performed before making request. If API not reachable, raises ValueError.
        
        Args:
            text: Text to summarize
            max_tokens: Maximum tokens in the response
        
        Returns:
            Generated summary
        
        Raises:
            ValueError: If API not reachable, no API key, or call fails
        """
        if not self.api_key:
            raise ValueError("GEMMA4_API_KEY not provided or found in environment")
        
        if not text or text.strip() == "":
            raise ValueError("Text to summarize cannot be empty")
        
        # Quick health check - if API not responding, fail immediately instead of hanging
        if not self._check_api_health():
            raise ValueError("Gemma4 API not reachable - check connectivity or try again later")
        
        # API is healthy, make the summarization request
        return self._call_api(text, max_tokens)
    
    def _call_api(self, text: str, max_tokens: int) -> str:
        """
        Internal method to call Gemma4 API.
        
        Args:
            text: Text to summarize
            max_tokens: Maximum tokens in the response
            
        Returns:
            Generated summary
            
        Raises:
            ValueError: If API call fails
        """
        # Craft the prompt for summarization
        prompt = f"""Genera un resumen conciso y claro del siguiente texto. 
El resumen debe ser breve pero completo, capturando los puntos principales.

TEXTO A RESUMIR:
{text}

RESUMEN:"""
        
        try:
            response = requests.post(
                f"{self.API_BASE_URL}/chat/completions",
                headers={
                    "Authorization": f"Bearer {self.api_key}",
                    "Content-Type": "application/json"
                },
                json={
                    "model": self.MODEL,
                    "messages": [
                        {"role": "user", "content": prompt}
                    ],
                    "temperature": 0.7,
                    "max_tokens": max_tokens
                },
                timeout=self.API_TIMEOUT
            )
            
            if response.status_code != 200:
                raise ValueError(f"API error {response.status_code}: {response.text}")
            
            data = response.json()
            
            # Extract summary from response
            # Some models use "content", others use "reasoning" for their output
            if "choices" in data and len(data["choices"]) > 0:
                choice = data["choices"][0]["message"]
                # Try content first, then reasoning if content is empty
                summary = (choice.get("content") or "").strip()
                if not summary:
                    summary = (choice.get("reasoning") or "").strip()
                
                if not summary:
                    raise ValueError("API returned no content or reasoning")
                
                return summary
            else:
                raise ValueError("Unexpected API response format")
        
        except requests.exceptions.Timeout:
            raise ValueError(f"Gemma4 API timeout (>{self.API_TIMEOUT}s) - request too slow")
        except requests.exceptions.RequestException as e:
            raise ValueError(f"Failed to call AI API: {str(e)}")
        except Exception as e:
            raise ValueError(f"Error generating summary: {str(e)}")
    
    def test_connection(self) -> bool:
        """
        Test if API connection works by sending a health check.
        
        Returns:
            True if connection successful, False if not reachable
        """
        if not self.api_key:
            raise ValueError("GEMMA4_API_KEY not provided or found in environment")
        
        return self._check_api_health()
