from fastapi import APIRouter
from pydantic import BaseModel
from ..services.ai_service import AIService

ai_router = APIRouter()
ai_service = AIService()

class QueryRequest(BaseModel):
    prompt: str

class QueryResponse(BaseModel):
    response: str

@ai_router.post("/query", response_model=QueryResponse)
async def query(request: QueryRequest):
    response = ai_service.query(request.prompt)
    return QueryResponse(response=response)
