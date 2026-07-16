/**
 * Creates minimal placeholder PNGs if missing (Expo requires icon/splash paths).
 */
const fs = require("fs");
const path = require("path");

const dir = path.join(__dirname, "..", "assets");
const files = ["icon.png", "splash-icon.png", "adaptive-icon.png"];

// 1x1 PNG (dark pixel)
const PNG = Buffer.from(
  "iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAADUlEQVR42mP8z8BQDwAEhQGAhKmMIQAAAABJRU5ErkJggg==",
  "base64"
);

if (!fs.existsSync(dir)) fs.mkdirSync(dir, { recursive: true });
for (const f of files) {
  const p = path.join(dir, f);
  if (!fs.existsSync(p)) fs.writeFileSync(p, PNG);
}
