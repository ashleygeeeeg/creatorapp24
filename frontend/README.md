# Frontend

The full React app lives in **Clone**. Sync into this repo:

```bash
bash scripts/mirror-from-clone.sh
```

Or clone Clone and push to creatorapp24:

```bash
git clone https://github.com/ashleygeeeeg/Clone.git
cd Clone
git remote add creator https://github.com/ashleygeeeeg/creatorapp24.git
git push creator main:main
```

Deploy on Vercel with **Root Directory** = `frontend`.
