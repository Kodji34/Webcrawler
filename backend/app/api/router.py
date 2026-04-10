from fastapi import APIRouter

from backend.app.api.routes.corpus import router as corpus_router
from backend.app.api.routes.fulltext import router as fulltext_router
from backend.app.api.routes.health import router as health_router
from backend.app.api.routes.pdf import router as pdf_router
from backend.app.api.routes.scientific import router as scientific_router
from backend.app.api.routes.web import router as web_router

api_router = APIRouter()
api_router.include_router(health_router, tags=["health"])
api_router.include_router(scientific_router, prefix="/scientific", tags=["scientific"])
api_router.include_router(fulltext_router, prefix="/fulltext", tags=["fulltext"])
api_router.include_router(pdf_router, prefix="/pdf", tags=["pdf"])
api_router.include_router(web_router, prefix="/web", tags=["web"])
api_router.include_router(corpus_router, prefix="/corpus", tags=["corpus"])
