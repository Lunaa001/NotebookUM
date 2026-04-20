from config import Config

def create_app(config_class=Config):
    from flask import Flask
    from .controllers import register_blueprints

    app = Flask(__name__)
    app.config.from_object(config_class)
    
    # Inicializar extensiones aquí si las hay
    
    # Registrar blueprints
    register_blueprints(app)
    
    return app
