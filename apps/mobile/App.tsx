import { useMemo, useState } from "react";
import {
  Pressable,
  StyleSheet,
  Text,
  View,
  ActivityIndicator,
} from "react-native";
import { StatusBar } from "expo-status-bar";
import { SafeAreaProvider, SafeAreaView } from "react-native-safe-area-context";
import { WebView } from "react-native-webview";
import Constants from "expo-constants";

const TABS = [
  { key: "home", label: "Home", path: "/" },
  { key: "auth", label: "Login", path: "/auth" },
  { key: "dashboard", label: "Dashboard", path: "/dashboard" },
  { key: "chat", label: "Wingman", path: "/chat" },
] as const;

type TabKey = (typeof TABS)[number]["key"];

function baseUrl(): string {
  const extra = Constants.expoConfig?.extra as { webBaseUrl?: string } | undefined;
  const fromEnv = process.env.EXPO_PUBLIC_WEB_URL;
  const raw = fromEnv || extra?.webBaseUrl || "http://localhost:3000";
  return raw.replace(/\/$/, "");
}

export default function App() {
  const [tab, setTab] = useState<TabKey>("home");
  const [loading, setLoading] = useState(true);
  const uri = useMemo(() => {
    const path = TABS.find((t) => t.key === tab)?.path ?? "/";
    return `${baseUrl()}${path}`;
  }, [tab]);

  return (
    <SafeAreaProvider>
      <SafeAreaView style={styles.root} edges={["top"]}>
        <StatusBar style="light" />
        <View style={styles.webWrap}>
          {loading ? (
            <View style={styles.loader}>
              <ActivityIndicator color="#22c55e" size="large" />
              <Text style={styles.loaderText}>Loading maligeeAi…</Text>
              <Text style={styles.hint}>{uri}</Text>
            </View>
          ) : null}
          <WebView
            key={uri}
            source={{ uri }}
            style={styles.web}
            onLoadStart={() => setLoading(true)}
            onLoadEnd={() => setLoading(false)}
            onError={() => setLoading(false)}
            javaScriptEnabled
            domStorageEnabled
            sharedCookiesEnabled
            startInLoadingState
          />
        </View>
        <View style={styles.tabBar}>
          {TABS.map((t) => (
            <Pressable
              key={t.key}
              onPress={() => setTab(t.key)}
              style={[styles.tab, tab === t.key && styles.tabActive]}
            >
              <Text style={[styles.tabText, tab === t.key && styles.tabTextActive]}>
                {t.label}
              </Text>
            </Pressable>
          ))}
        </View>
      </SafeAreaView>
    </SafeAreaProvider>
  );
}

const styles = StyleSheet.create({
  root: { flex: 1, backgroundColor: "#0a0a0a" },
  webWrap: { flex: 1, position: "relative" },
  web: { flex: 1, backgroundColor: "#0a0a0a" },
  loader: {
    ...StyleSheet.absoluteFillObject,
    zIndex: 2,
    alignItems: "center",
    justifyContent: "center",
    backgroundColor: "#0a0a0a",
    padding: 24,
  },
  loaderText: { color: "#e5e5e5", marginTop: 12, fontSize: 16 },
  hint: { color: "#737373", marginTop: 8, fontSize: 11, textAlign: "center" },
  tabBar: {
    flexDirection: "row",
    borderTopWidth: 1,
    borderTopColor: "#262626",
    backgroundColor: "#141414",
  },
  tab: { flex: 1, paddingVertical: 12, alignItems: "center" },
  tabActive: { borderTopWidth: 2, borderTopColor: "#22c55e" },
  tabText: { color: "#a3a3a3", fontSize: 11, fontWeight: "600" },
  tabTextActive: { color: "#22c55e" },
});
