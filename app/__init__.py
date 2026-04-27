from fastapi import FastAPI
from .controllers import register_routers

def create_app():
    app = FastAPI()
    
    # Registrar routers
    register_routers(app)
    
    return app
