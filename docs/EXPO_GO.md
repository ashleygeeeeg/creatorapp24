# Link CreatorApp24 to Expo Go

## 1. One-time setup

```bash
cd creatorapp24/apps/mobile
cp .env.example .env
npm install
npx expo login
```

Use your [expo.dev](https://expo.dev) account (create one free if needed). Logging in links your dev session to Expo Go on your phone when you use the same account.

## 2. Set the web app URL (WebView target)

Edit `apps/mobile/.env`:

```env
# Production (recommended — works from anywhere in Expo Go)
EXPO_PUBLIC_WEB_URL=https://YOUR_VERCEL_APP.vercel.app

# OR local dev (phone must reach your PC)
# EXPO_PUBLIC_WEB_URL=http://192.168.1.XXX:3000
```

Restart Metro after changing `.env`.

## 3. Start and link Expo Go

**Option A — same Wi‑Fi (fastest)**
```bash
npm run go
# or: npx expo start --go
```

**Option B — tunnel (phone on cellular / different network)**
```bash
npm run tunnel
# or: npx expo start --tunnel
```
First run may install `@expo/ngrok`; accept prompts.

## 4. Open on your phone

1. Install **Expo Go** ([iOS](https://apps.apple.com/app/expo-go/id982107779) / [Android](https://play.google.com/store/apps/details?id=host.exp.exponent)).
2. **Android:** Expo Go → **Scan QR code** from the terminal or `http://localhost:8081`.
3. **iOS:** Camera app → scan QR → **Open in Expo Go**.
4. Optional: Expo Go → **Log in** with the same expo.dev account as step 1.

You should see the maligeeAi WebView with bottom tabs (Home, Login, Dashboard, Wingman).

## 5. Open via link (manual)

With Metro running, the terminal shows something like:

```text
exp://192.168.x.x:8081
```

On a device with Expo Go installed, you can paste that URL in Safari/Chrome or use **Enter URL manually** in Expo Go (Android).

Tunnel mode shows an `exp://u.expo.dev/...` style URL — use that when not on LAN.

## 6. Local web + API checklist

| Service | Command | Phone must reach |
|---------|---------|------------------|
| API | `docker compose up` (repo root) | `http://LAN_IP:8000` in `REACT_APP_BACKEND_URL` |
| Web | `cd frontend && yarn start` | `EXPO_PUBLIC_WEB_URL=http://LAN_IP:3000` |
| Expo | `cd apps/mobile && npm run tunnel` | QR / exp link only |

## Troubleshooting

| Problem | Fix |
|---------|-----|
| QR doesn’t open app | Use `npm run tunnel`; update Expo Go from store |
| “Could not connect” | Firewall: allow Node/Metro; try tunnel |
| White screen in WebView | Wrong `EXPO_PUBLIC_WEB_URL`; test URL in phone browser first |
| Stale bundle | Shake device → Reload; or `npx expo start -c` |

## Optional: EAS project ID

For builds later (not required for Expo Go):

```bash
npm install -g eas-cli
eas login
eas init
```

Add to `.env`:

```env
EXPO_PUBLIC_EAS_PROJECT_ID=your-uuid-from-eas
```
