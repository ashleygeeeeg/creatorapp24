# CreatorApp24 — Product roadmap

Develop this as a **real software project** in VS Code (or similar): run, test, and commit incrementally. Chat is for design, reviews, and targeted fixes—not assembling the full app file-by-file.

## Phase 1 — Foundation

| Step | Status | Notes |
|------|--------|--------|
| Initialize repository | ✅ | [creatorapp24](https://github.com/ashleygeeeeg/creatorapp24) |
| Create Next.js application | ⬜ | New `apps/web` or migrate from CRA in `frontend/` |
| Build IDE UI | ⬜ | Editor shell, file tree, preview |
| Integrate Geeus AI + Wingman | ⬜ | API keys via `.env`; align with existing Partner/Wingman concepts in Clone |
| Verify local run | ⬜ | `pnpm dev` / `npm run dev` + API |

**Reference:** Full-stack patterns in [Clone](https://github.com/ashleygeeeeg/Clone) (FastAPI + React). Phase 1 may **replace** CRA with Next.js per product direction.

## Phase 2 — SaaS

- Authentication (Supabase)
- Project storage
- User dashboard
- Settings
- Billing (Stripe)

## Phase 3 — Production

- Docker support (partial: `backend/Dockerfile`, `docker-compose.yml`)
- CI/CD (GitHub Actions)
- Monitoring & logging
- Security hardening
- Production deployment (Vercel + API host)

## Phase 4 — Mobile

- Expo companion app
- Project sync
- Push notifications
- AppCreator24 WebView shell → see `docs/APPMAKER24.md`

## How to use Grok in this workflow

- Implement a **single feature** or file with clear scope
- **Review** PRs or snippets
- **Debug** errors (paste logs + file)
- **Design** APIs and data models
- **UI** feedback on components
- **Deploy** checklists (Vercel, env, CORS)

Avoid: pasting entire monorepos or multi-hundred-line dumps in one message.
