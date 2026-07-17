# CreatorApp24 (maligeeAi)

**Production repository** for the CreatorApp24 / AppMaker24 product: web app + API + AppCreator24 Android WebView shell.

- **GitHub:** https://github.com/ashleygeeeeg/creatorapp24
- **Full UI mirror source:** https://github.com/ashleygeeeeg/Clone (use `scripts/mirror-from-clone.sh` to sync `frontend/`)

## Stack

| Layer | Path | Deploy |
|--------|------|--------|
| API | `backend/` | Docker / Railway / Render |
| Web | `frontend/` | Vercel (root dir `frontend`) |
| Mobile shell | AppCreator24 | WebView → your Vercel URL |
| DB | MongoDB | Atlas or `docker compose` |

## Quick start

```bash
cp .env.example .env
docker compose up --build
cd frontend && yarn install && yarn start
```

## Docs

- [`docs/ARCHITECTURE.md`](docs/ARCHITECTURE.md) — production layout
- [`docs/APPMAKER24.md`](docs/APPMAKER24.md) — link Android app
- [`contracts.md`](contracts.md) — API contracts

## Git remotes (local)

```bash
git remote add origin https://github.com/ashleygeeeeg/creatorapp24.git
git push -u origin main

## git remote set-url origin https://github.com/appcreators24/Clone.git
git add .
git commit -m "Initial commit"
git push -u origin main
```
