from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.controllers import health_controller
from config import settings

app = FastAPI(
    title=settings.APP_NAME, version=settings.VERSION, description="NotebookUM API"
)

# Configurar CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Registrar routers
app.include_router(health_controller.router, prefix="/api/v1", tags=["Health"])


@app.get("/")
async def root():
    return {
        "message": "Welcome to NotebookUM API",
        "version": settings.VERSION,
        "docs": "/docs",
    }


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(
        "main:app", host=settings.HOST, port=settings.PORT, reload=settings.DEBUG
    )
