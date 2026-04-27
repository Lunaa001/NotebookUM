from fastapi import APIRouter
from pydantic import BaseModel
import os
import openai

intelligence_router = APIRouter()


class ChatRequest(BaseModel):
    message: str


class ChatResponse(BaseModel):
    response: str


@intelligence_router.post("/chat", response_model=ChatResponse)
async def chat(request: ChatRequest):
    """Send a message to the Gemma model and return its response"""
    user_message = request.message
    
    # Configure OpenAI client with custom settings
    client = openai.OpenAI(
        api_key=os.getenv("GEMMA_API_KEY"),
        base_url=os.getenv("GEMMA_API_URL")
    )
    
    # Call the API
    completion = client.chat.completions.create(
        model="gemma3-4b",
        messages=[
            {"role": "user", "content": user_message}
        ]
    )
    
    response_text = completion.choices[0].message.content
    
    return ChatResponse(response=response_text)