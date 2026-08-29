import { Stack } from "expo-router";
import { StatusBar } from "expo-status-bar";
import { AnalysisProvider } from "@/src/context/AnalysisContext";
import { AuthProvider } from "@/src/context/AuthContext";
import { colors } from "@/src/config/theme";

export default function RootLayout() {
  const main = { headerShown: false };
  return (
    <AuthProvider>
      <AnalysisProvider>
        <StatusBar style="dark" />
        <Stack
          screenOptions={{
            animation: "slide_from_right",
            headerStyle: { backgroundColor: colors.card },
            headerShadowVisible: false,
            headerTintColor: colors.text,
            headerTitleStyle: { fontWeight: "700" },
            contentStyle: { backgroundColor: colors.background },
          }}
        >
          <Stack.Screen name="index" options={main} />
          <Stack.Screen name="exercises" options={main} />
          <Stack.Screen name="identify" options={main} />
          <Stack.Screen name="history" options={main} />
      <Stack.Screen name="more" options={main} />
      <Stack.Screen name="today" options={{ title: "Today's plan" }} />
      <Stack.Screen name="appointments" options={{ title: "Appointments" }} />
      <Stack.Screen name="notifications" options={{ title: "Notifications" }} />
      <Stack.Screen name="billing" options={{ title: "Sessions & packages" }} />
          <Stack.Screen name="exercise/[id]" options={{ title: "Exercise" }} />
          <Stack.Screen
            name="guidance/[id]"
            options={{ title: "Camera setup" }}
          />
          <Stack.Screen
            name="upload/[id]"
            options={{ title: "Review and analyze" }}
          />
          <Stack.Screen
            name="result"
            options={{ title: "Your results", headerBackVisible: false }}
          />
          <Stack.Screen name="login" options={{ title: "Log in" }} />
          <Stack.Screen name="register" options={{ title: "Create account" }} />
          <Stack.Screen
            name="forgot-password"
            options={{ title: "Password recovery" }}
          />
          <Stack.Screen
            name="reset-password"
            options={{ title: "Reset password" }}
          />
          <Stack.Screen
            name="verify-email"
            options={{ title: "Verify email" }}
          />
          <Stack.Screen name="profile" options={{ title: "Profile" }} />
          <Stack.Screen name="safety" options={{ title: "Safety & privacy" }} />
          <Stack.Screen
            name="limitations"
            options={{ title: "Known limitations" }}
          />
        </Stack>
      </AnalysisProvider>
    </AuthProvider>
  );
}
