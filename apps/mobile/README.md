# CreatorApp24 — Expo Go

WebView shell for maligeeAi (same idea as AppCreator24).

## Run in Expo Go

1. Install [Expo Go](https://expo.dev/go) on your phone.
2. Start your **web** app (CRA from Clone or future Next.js):
   ```bash
   cd frontend && yarn start
   ```
3. Copy `.env.example` → `.env` and set your computer's LAN IP:
   ```bash
   cd apps/mobile
   cp .env.example .env
   # EXPO_PUBLIC_WEB_URL=http://YOUR_LAN_IP:3000
   ```
4. Install and start Metro:
   ```bash
   npm install
   npx expo start
   ```
5. Scan the QR code with Expo Go (Android) or Camera (iOS).

## Production

Point `EXPO_PUBLIC_WEB_URL` at your Vercel URL (HTTPS).

## Troubleshooting

| Issue | Fix |
|-------|-----|
| Blank / can't connect | Phone and PC on same Wi‑Fi; use LAN IP not `localhost` |
| API errors in WebView | Set `REACT_APP_BACKEND_URL` to LAN API or HTTPS API |
| CORS | Add your origin to backend `CORS_ORIGINS` |
