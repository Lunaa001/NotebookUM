from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.controllers import register_routers
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

# Registrar todos los routers
register_routers(app)


@app.get("/")
async def root():
    return {
        "message": "Welcome to NotebookUM API",
        "version": settings.VERSION,
        "docs": "/docs",
    }
