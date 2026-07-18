import { Stack } from "expo-router";
import { StatusBar } from "expo-status-bar";
import { AnalysisProvider } from "@/src/context/AnalysisContext";
import { AuthProvider } from "@/src/context/AuthContext";
import { colors } from "@/src/config/theme";

export default function RootLayout() {
  return <AuthProvider><AnalysisProvider><StatusBar style="dark" /><Stack screenOptions={{ headerStyle: { backgroundColor: colors.card }, headerTintColor: colors.text, headerTitleStyle: { fontWeight: "700" }, contentStyle: { backgroundColor: colors.background } }}><Stack.Screen name="index" options={{ headerShown: false }} /><Stack.Screen name="exercises" options={{ title: "Exercise Library" }} /><Stack.Screen name="exercise/[id]" options={{ title: "Exercise Details" }} /><Stack.Screen name="guidance/[id]" options={{ title: "Camera Guidance" }} /><Stack.Screen name="upload/[id]" options={{ title: "Upload Video" }} /><Stack.Screen name="result" options={{ title: "Analysis Result", headerBackVisible: false }} /><Stack.Screen name="history" options={{ title: "Session History" }} /><Stack.Screen name="login" options={{ title: "Log In" }} /><Stack.Screen name="register" options={{ title: "Create Demo Account" }} /><Stack.Screen name="profile" options={{ title: "Profile" }} /><Stack.Screen name="safety" options={{ title: "Safety & Privacy" }} /><Stack.Screen name="limitations" options={{ title: "Known Limitations" }} /></Stack></AnalysisProvider></AuthProvider>;
}
