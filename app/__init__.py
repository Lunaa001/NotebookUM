from flask import Flask
from config import Config
from .controllers import register_blueprints

def create_app(config_class=Config):
    app = Flask(__name__)
    app.config.from_object(config_class)
    
    # Inicializar extensiones aquí si las hay
    
    # Registrar blueprints
    register_blueprints(app)
    
    return app