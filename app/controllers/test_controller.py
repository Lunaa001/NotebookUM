"""Test endpoint for AI summarization - temporary for development"""

from fastapi import APIRouter, HTTPException, status
from pydantic import BaseModel
from app.services.ai_service import AIService
import os

test_router = APIRouter(prefix="/api/v1/test", tags=["test"])


class SummarizeTestRequest(BaseModel):
    """Test request for summarization"""
    text: str
    max_tokens: int = 200


class SummarizeTestResponse(BaseModel):
    """Test response for summarization"""
    status: str
    summary: str
    length: int


@test_router.post("/summarize", response_model=SummarizeTestResponse)
async def test_summarize(request: SummarizeTestRequest):
    """
    Test endpoint for AI summarization
    
    **Development only** - Remove in production
    
    Args:
        text: Text to summarize
        max_tokens: Maximum tokens in response
    
    Returns:
        Summary and metadata
    """
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="OPENAI_API_KEY not configured"
        )
    
    try:
        service = AIService(api_key=api_key)
        summary = service.generate_summary(request.text, max_tokens=request.max_tokens)
        
        return SummarizeTestResponse(
            status="success",
            summary=summary,
            length=len(summary)
        )
    
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Summarization failed: {str(e)}"
        )


@test_router.post("/ai/connection-test")
async def test_ai_connection():
    """
    Test if AI API connection works
    
    **Development only** - Remove in production
    """
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="OPENAI_API_KEY not configured"
        )
    
    try:
        service = AIService(api_key=api_key)
        result = service.test_connection()
        
        return {
            "status": "success" if result else "failed",
            "connected": result,
            "endpoint": "https://ai.cloud.um.edu.ar/api/v1/chat/completions",
            "model": "gemma4-26b"
        }
    
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )
