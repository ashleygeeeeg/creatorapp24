# Run in Expo Go

## Quick steps

```bash
git pull origin main
cd creatorapp24/apps/mobile
cp .env.example .env
# Edit EXPO_PUBLIC_WEB_URL — use https://your-app.vercel.app OR http://192.168.x.x:3000
npm install
npx expo start
```

Open **Expo Go** on your phone and scan the QR code.

## Two-server local setup

**Terminal 1 — API**
```bash
cd creatorapp24
docker compose up
```

**Terminal 2 — Web (sync from Clone if needed)**
```bash
bash scripts/mirror-from-clone.sh
cd frontend
# frontend/.env.local: REACT_APP_BACKEND_URL=http://YOUR_LAN_IP:8000
yarn install && yarn start --host 0.0.0.0
```

**Terminal 3 — Expo**
```bash
cd apps/mobile
EXPO_PUBLIC_WEB_URL=http://YOUR_LAN_IP:3000 npx expo start
```

Replace `YOUR_LAN_IP` with your machine's address (`ipconfig` / `ifconfig`).

## Easiest path (no LAN)

Deploy web to Vercel, then in `apps/mobile/.env`:

```env
EXPO_PUBLIC_WEB_URL=https://your-app.vercel.app
```

Expo Go only loads the WebView; no rebuild needed when you change the website.
