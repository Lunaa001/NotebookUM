from .example_controller import example_router
from .ai_controller import ai_router


def register_routers(app):
    app.include_router(example_router, prefix="/api/example", tags=["example"])
    app.include_router(ai_router, prefix="/api/ai", tags=["ai"])
