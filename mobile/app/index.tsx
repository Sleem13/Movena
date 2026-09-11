import { Redirect } from "expo-router";
import { useAuth } from "@/src/context/AuthContext";
import { AppShell } from "@/src/components/AppShell";
import { Loading } from "@/src/components/UI";
import { homeRoute } from "@/src/utils/care";

export default function HomeScreen() {
  const { user, loading } = useAuth();
  if (loading) return <AppShell active="today"><Loading label="Opening Movena" /></AppShell>;
  return <Redirect href={user ? homeRoute(user.role) : "/today"} />;
}
