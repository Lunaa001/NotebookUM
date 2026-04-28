"""Service for AI-powered text summarization using UM Gemma4 API"""

import requests
from typing import Optional
import os
import logging
from app.services.circuit_breaker_service import CircuitBreakerFactory

logger = logging.getLogger(__name__)


class AIService:
    """Service for calling UM Gemma4 API for summarization"""
    
    # UM AI Cloud configuration
    API_BASE_URL = "https://ai.cloud.um.edu.ar/api/v1"
    MODEL = "gemma4-26b-16g"
    CIRCUIT_BREAKER_NAME = "gemma4_api"
    
    def __init__(self, api_key: Optional[str] = None):
        """
        Initialize AI Service with API key and Circuit Breaker
        
        Args:
            api_key: UM AI API key (or from env variable GEMMA4_API_KEY)
        """
        self.api_key = api_key or os.getenv("GEMMA4_API_KEY")
        # Initialize circuit breaker for API calls
        # fail_max=5: Open after 5 failures
        # reset_timeout=30: Wait 30s before attempting recovery
        self.circuit_breaker = CircuitBreakerFactory.get_or_create(
            name=self.CIRCUIT_BREAKER_NAME,
            fail_max=5,
            reset_timeout=30,
        )
    
    def generate_summary(self, text: str, max_tokens: int = 200) -> str:
        """
        Generate a summary of the provided text using Gemma4 with Circuit Breaker protection
        
        Args:
            text: Text to summarize
            max_tokens: Maximum tokens in the response
        
        Returns:
            Generated summary
        
        Raises:
            ValueError: If API call fails, circuit is open, or no API key available
        """
        if not self.api_key:
            raise ValueError("GEMMA4_API_KEY not provided or found in environment")
        
        if not text or text.strip() == "":
            raise ValueError("Text to summarize cannot be empty")
        
        # Execute with circuit breaker protection
        try:
            return self.circuit_breaker.call(self._call_api, text, max_tokens)
        except Exception as e:
            logger.error(f"Failed to generate summary: {str(e)}")
            raise
    
    def _call_api(self, text: str, max_tokens: int) -> str:
        """
        Internal method to call Gemma4 API (wrapped by circuit breaker)
        
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
                timeout=30
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
        
        except requests.exceptions.RequestException as e:
            raise ValueError(f"Failed to call AI API: {str(e)}")
        except Exception as e:
            raise ValueError(f"Error generating summary: {str(e)}")
    
    def test_connection(self) -> bool:
        """
        Test if API connection works with Circuit Breaker protection
        
        Returns:
            True if connection successful
        
        Raises:
            ValueError: If connection fails or no API key available
        """
        if not self.api_key:
            raise ValueError("GEMMA4_API_KEY not provided or found in environment")
        
        # Execute with circuit breaker protection
        return self.circuit_breaker.call(self._test_connection_api)
    
    def _test_connection_api(self) -> bool:
        """
        Internal method to test API connection (wrapped by circuit breaker)
        
        Returns:
            True if connection successful
            
        Raises:
            ValueError: If connection fails
        """
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
                        {"role": "user", "content": "Hola"}
                    ],
                    "max_tokens": 10
                },
                timeout=10
            )
            
            return response.status_code == 200
        
        except Exception as e:
            raise ValueError(f"API connection failed: {str(e)}")
