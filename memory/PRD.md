# maligeeAi — PRD

## Original Problem Statement
Clone emergent.sh website, rebrand as "maligeeAi", and build a full-stack platform:
- Real JWT authentication (signup/login)
- Mock billing for app builds: 1st build free, $10/build after, edits free (real Stripe to be added later when user provides keys)
- Unfiltered AI chat/code generator named "Partner in Crime" (Emergent LLM key, GPT-4o)
- Spinning "MG.AI" logo in Space Grotesk font

## Tech Stack
React + Tailwind (frontend), FastAPI (backend), MongoDB. JWT auth. Emergent LLM key for AI chat.

## Implemented (as of June 2026)
- Landing page: hero w/ spinning MG.AI logo, features, showcase carousel, waitlist, footer
- JWT auth: signup, login, /api/auth/me, protected routes
- Dashboard: build management, mock payment ($10 after first free build), deploy
- "Partner in Crime" AI chat (GPT-4o via Emergent LLM key)
- Deployment health check passed
- Full E2E regression after GitHub repo sync: 24/24 backend tests + all frontend flows passed (test_reports/iteration_1.json)
- Chat History on Dashboard: "Recent Conversations" section, cards open /chat?session={id} and hydrate past messages (verified)
- Build Sharing: POST /api/builds/{id}/share generates stable slug; public page /share/{slug} (no auth) with build info + CTA; Share button with copy-to-clipboard on deployed builds (31/31 backend tests + frontend flows verified, test_reports/iteration_2.json)

## Key Endpoints
- POST /api/auth/signup, /api/auth/login, GET /api/auth/me
- GET/POST /api/builds, POST /api/builds/{id}/pay, POST /api/builds/{id}/share
- GET /api/share/{slug} (public)
- POST /api/chat, POST /api/waitlist
- GET /api/showcase, /api/features

## Mocked
- Payment gateway (MOCKED intentionally; user will add real Stripe later)

## Backlog
- P1: Real Stripe integration (awaiting user's Stripe account/keys)
- P2: Add data-testid attributes across interactive elements for robust automated testing
- P2: Split server.py (~613 lines) into routers (auth, builds, chat, landing)
