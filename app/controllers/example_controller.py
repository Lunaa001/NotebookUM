from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import Optional, Any
from ..services.example_service import ExampleService

example_router = APIRouter()
example_service = ExampleService()

class ExampleResponse(BaseModel):
    success: bool
    data: Optional[Any] = None
    message: Optional[str] = None

@example_router.get('/', response_model=ExampleResponse)
async def get_all():
    data = example_service.get_all()
    return ExampleResponse(success=True, data=data)

@example_router.get('/{id}', response_model=ExampleResponse)
async def get_one(id: int):
    data = example_service.get_by_id(id)
    if data:
        return ExampleResponse(success=True, data=data)
    raise HTTPException(status_code=404, detail="Not found")

@example_router.post('/', response_model=ExampleResponse, status_code=201)
async def create(data: dict):
    result = example_service.create(data)
    return ExampleResponse(success=True, data=result)

@example_router.put('/{id}', response_model=ExampleResponse)
async def update(id: int, data: dict):
    result = example_service.update(id, data)
    if result:
        return ExampleResponse(success=True, data=result)
    raise HTTPException(status_code=404, detail="Not found")

@example_router.delete('/{id}', response_model=ExampleResponse)
async def delete(id: int):
    result = example_service.delete(id)
    if result:
        return ExampleResponse(success=True, message="Deleted successfully")
    raise HTTPException(status_code=404, detail="Not found")