"""Service for AI-powered text summarization using UM Gemma4 API"""

import requests
from typing import Optional
import os


class AIService:
    """Service for calling UM Gemma4 API for summarization"""
    
    # UM AI Cloud configuration
    API_BASE_URL = "https://ai.cloud.um.edu.ar/api/v1"
    MODEL = "gemma4-26b-16g"
    
    def __init__(self, api_key: Optional[str] = None):
        """
        Initialize AI Service with API key
        
        Args:
            api_key: UM AI API key (or from env variable GEMMA4_API_KEY)
        """
        self.api_key = api_key or os.getenv("GEMMA4_API_KEY")
    
    def generate_summary(self, text: str, max_tokens: int = 200) -> str:
        """
        Generate a summary of the provided text using Gemma4
        
        Args:
            text: Text to summarize
            max_tokens: Maximum tokens in the response
        
        Returns:
            Generated summary
        
        Raises:
            ValueError: If API call fails or no API key available
        """
        if not self.api_key:
            raise ValueError("GEMMA4_API_KEY not provided or found in environment")
        
        if not text or text.strip() == "":
            raise ValueError("Text to summarize cannot be empty")
        
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
        Test if API connection works
        
        Returns:
            True if connection successful
        
        Raises:
            ValueError: If connection fails or no API key available
        """
        if not self.api_key:
            raise ValueError("GEMMA4_API_KEY not provided or found in environment")
        
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
