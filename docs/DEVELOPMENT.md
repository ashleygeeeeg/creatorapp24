# Local development

## Prerequisites

- Node 20+ (pnpm or yarn recommended)
- Python 3.11+ (API)
- MongoDB (local Docker or Atlas)
- Git

## Clone

```bash
git clone https://github.com/ashleygeeeeg/creatorapp24.git
cd creatorapp24
cp .env.example .env
# fill MONGO_URL, JWT_SECRET, EMERGENT_LLM_KEY, etc.
```

## API (current FastAPI stack)

```bash
docker compose up --build
# API: http://localhost:8000
# Docs: http://localhost:8000/docs
```

## Frontend (today)

`frontend/` is a **placeholder** until Phase 1 Next.js IDE lands. To run the legacy CRA UI from Clone:

```bash
bash scripts/mirror-from-clone.sh
cd frontend && yarn install && yarn start
```

Set `frontend/.env.local` from `frontend/.env.example`.

## Phase 1 — Next.js (recommended layout)

When you scaffold Next.js, consider:

```text
creatorapp24/
  apps/web/          # Next.js IDE + marketing
  packages/ui/       # shared components (optional)
  backend/           # FastAPI (unchanged until merge/rename)
```

Use `pnpm create next-app` or `npx create-next-app@latest` inside `apps/web`.

## Git workflow

```bash
git checkout -b feature/phase1-next-shell
# small commits
git push -u origin feature/phase1-next-shell
```

Open PRs on GitHub; use chat for review before merge.

## Related repos

| Repo | Role |
|------|------|
| **creatorapp24** | Production target |
| **Clone** | Reference implementation (CRA + full pages) |
