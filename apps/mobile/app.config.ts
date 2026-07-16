import { ExpoConfig, ConfigContext } from "expo/config";

export default ({ config }: ConfigContext): ExpoConfig => ({
  ...config,
  name: "CreatorApp24",
  slug: "creatorapp24",
  extra: {
    webBaseUrl:
      process.env.EXPO_PUBLIC_WEB_URL ?? "http://localhost:3000",
  },
});
