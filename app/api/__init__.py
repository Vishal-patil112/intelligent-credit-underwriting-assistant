from app.api.applications import router as applications_router
from app.api.documents import router as documents_router
from app.api.review import router as review_router
from app.api.underwriting import router as underwriting_router

__all__ = ['applications_router', 'documents_router', 'review_router', 'underwriting_router']
