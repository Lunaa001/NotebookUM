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
    """Send a message to the OpenAI-compatible API from UM AI Cloud"""
    user_message = request.message
    
    # Configure OpenAI client with UM AI Cloud settings
    client = openai.OpenAI(
        api_key=os.getenv("OPENAI_API_KEY"),
        base_url=os.getenv("OPENAI_API_BASE_URL", "https://ai.cloud.um.edu.ar/api/v1")
    )
    
    # Call the API
    completion = client.chat.completions.create(
        model="gemma4-26b",
        messages=[
            {"role": "user", "content": user_message}
        ]
    )
    
    response_text = completion.choices[0].message.content
    
    return ChatResponse(response=response_text)