# CreatorApp24 API route modules
from .appmaker24 import register as register_appmaker24_routes
from .system import router as system_router

__all__ = ["register_appmaker24_routes", "system_router"]
