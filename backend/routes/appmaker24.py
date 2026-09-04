import os
from fastapi import APIRouter

from routes.agent import register as register_agent_routes


def register(router: APIRouter) -> None:
    """Register AppCreator24 / appmaker24 WebView URL manifest on the main API router."""

    @router.get("/integrations/appmaker24")
    async def get_appmaker24_integration():
        public_web = (
            os.environ.get("PUBLIC_WEB_URL") or "https://YOUR_VERCEL_URL.vercel.app"
        ).rstrip("/")
        api_public = (
            os.environ.get("PUBLIC_API_URL")
            or os.environ.get("BACKEND_PUBLIC_URL")
            or "http://localhost:8000"
        ).rstrip("/")
        android_app = (
            os.environ.get("APPCREATOR24_APP_URL") or "https://www.appcreator24.com"
        ).rstrip("/")
        return {
            "brand": "maligeeAi",
            "platform": "AppCreator24",
            "aliases": ["appmaker24", "appcreator24"],
            "android_shell_url": android_app,
            "public_web_url": public_web,
            "api_url": f"{api_public}/api",
            "webview_menus": [
                {"title": "Home", "path": "/", "url": f"{public_web}/"},
                {"title": "Login", "path": "/auth", "url": f"{public_web}/auth"},
                {"title": "Dashboard", "path": "/dashboard", "url": f"{public_web}/dashboard"},
                {"title": "Partner in Crime", "path": "/chat", "url": f"{public_web}/chat"},
                {"title": "AI Code Workspace", "path": "/workspace", "url": f"{public_web}/workspace"},
            ],
            "docs": "https://github.com/ashleygeeeeg/creatorapp24/blob/main/docs/APPMAKER24.md",
        }

    # Keep route registration modular without changing server.py's startup contract.
    register_agent_routes(router)
