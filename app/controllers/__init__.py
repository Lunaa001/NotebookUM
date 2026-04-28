from .example_controller import example_router
from .ai_controller import ai_router
from .users import users_router
from .summaries import summaries_router
from .intelligence import intelligence_router
from .main import main_router
from .documents import documents_router
from .test_controller import test_router


def register_routers(app):
    app.include_router(example_router, prefix="/api/v1/example", tags=["example"])
    app.include_router(ai_router, prefix="/api/v1/ai", tags=["ai"])
    app.include_router(users_router, prefix="/api/v1/users", tags=["users"])
    app.include_router(summaries_router, prefix="/api/v1/summaries", tags=["summaries"])
    app.include_router(intelligence_router, prefix="/api/v1", tags=["intelligence"])
    app.include_router(main_router, tags=["main"])
    app.include_router(documents_router, prefix="/api/v1/documents", tags=["documents"])
    app.include_router(test_router, tags=["test"])  # Dev endpoints only
