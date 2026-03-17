from .example_controller import example_bp
from .ai_controller import ai_bp


def register_blueprints(app):
    app.register_blueprint(example_bp, url_prefix="/api/example")
    app.register_blueprint(ai_bp, url_prefix="/api/ai")
