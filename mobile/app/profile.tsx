import { useRouter } from "expo-router";
import { Body, Card, Loading, PrimaryButton, SafetyNotice, Screen, StatusBadge, Title } from "@/src/components/UI";
import { useAuth } from "@/src/context/AuthContext";

export default function ProfileScreen() {
  const router = useRouter(); const { user, loading, signOut } = useAuth();
  if (loading) return <Screen><Loading label="Checking login" /></Screen>;
  if (!user) return <Screen><Title>Profile</Title><Body muted>Log in to save and review protected development session metadata.</Body><PrimaryButton title="Log in" onPress={() => router.push("/login")} /><PrimaryButton title="Continue in demo mode" onPress={() => router.replace("/exercises")} secondary /><SafetyNotice /></Screen>;
  return <Screen><StatusBadge label={user.role} tone="blue" /><Title>{user.full_name || "Movena user"}</Title><Card><Body>{user.email}</Body><Body muted>Session tokens are stored with Expo SecureStore on this device.</Body></Card><PrimaryButton title="View session history" onPress={() => router.push("/history")} /><PrimaryButton title="Log out" onPress={async () => { await signOut(); router.replace("/exercises"); }} secondary /><SafetyNotice /></Screen>;
}
