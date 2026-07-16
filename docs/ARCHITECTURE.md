# Production architecture — CreatorApp24

## Overview

```
[AppCreator24 Android] --WebView--> [Vercel: React SPA]
                                           |
                                           v
                                    [FastAPI API]
                                           |
                                           v
                                      [MongoDB]
```

## Services

### 1. Frontend (`frontend/`)
- React 19 + CRA/Craco + Tailwind
- Routes: `/`, `/auth`, `/dashboard`, `/chat`
- Env: `REACT_APP_BACKEND_URL`, `REACT_APP_APPCREATOR24_APP_URL`
- Deploy: Vercel, output `build/`

### 2. API (`backend/server.py`)
- Auth (JWT), builds/billing (mock pay), waitlist, landing data, AI chat
- Integration: `GET /api/integrations/appmaker24` for WebView menu URLs
- Env: `MONGO_URL`, `JWT_SECRET`, `EMERGENT_LLM_KEY`, `PUBLIC_WEB_URL`, `PUBLIC_API_URL`, `APPCREATOR24_APP_URL`, `CORS_ORIGINS`

### 3. MongoDB
- Collections: users, builds, payments, waitlist, showcase, features, stats, chat_history

### 4. AppCreator24 (external)
- No-code Android shell; menus open HTTPS routes on your Vercel domain

## Deployment order

1. Deploy API with HTTPS + MongoDB
2. Deploy frontend; set `REACT_APP_BACKEND_URL`
3. Set backend `PUBLIC_WEB_URL` and `CORS_ORIGINS`
4. Configure AppCreator24 WebView URLs (see `docs/APPMAKER24.md`)
5. Set `APPCREATOR24_APP_URL` on API + frontend

## Repos

| Repo | Role |
|------|------|
| **creatorapp24** | Production target (this repo) |
| **Clone** | Full application source; mirror into `frontend/` when needed |
