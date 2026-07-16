import { ExpoConfig, ConfigContext } from "expo/config";

export default ({ config }: ConfigContext): ExpoConfig => {
  const webBaseUrl =
    process.env.EXPO_PUBLIC_WEB_URL ?? "https://your-app.vercel.app";

  return {
    ...config,
    name: "CreatorApp24",
    slug: "creatorapp24",
    scheme: "creatorapp24",
    extra: {
      webBaseUrl: webBaseUrl.replace(/\/$/, ""),
      eas: {
        projectId: process.env.EXPO_PUBLIC_EAS_PROJECT_ID ?? undefined,
      },
    },
  };
};
