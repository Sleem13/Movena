import { View } from "react-native";
import { useRouter } from "expo-router";

import { AppShell, BrandHeader } from "@/src/components/AppShell";
import { ActionRow, SectionTitle } from "@/src/components/GuidedUI";
import { Body, Card, Loading, PrimaryButton, StatusBadge } from "@/src/components/UI";
import { useAuth } from "@/src/context/AuthContext";
import { homeRoute, isAdministrator, isTherapist, roleLabel } from "@/src/utils/care";

export default function ProfileScreen() {
  const router = useRouter();
  const { user, loading, signOut } = useAuth();
  if (loading) return <AppShell active="more"><Loading label="Checking login" /></AppShell>;
  if (!user) return <AppShell active="more"><BrandHeader title="Your profile" subtitle="Log in to open your Movena workspace." /><PrimaryButton title="Log in" onPress={() => router.push("/login")} /><PrimaryButton title="Create account" secondary onPress={() => router.push("/register")} /></AppShell>;

  const therapist = isTherapist(user.role);
  const administrator = isAdministrator(user.role);
  const workspaceTitle = therapist ? "Therapist workspace" : administrator ? "Clinical administration" : user.role === "patient" ? "Your recovery workspace" : "Team workspace";
  const workspaceDetail = therapist
    ? "Review patients, follow-ups, and your schedule."
    : administrator
      ? "Oversee patient care, clinical reviews, and appointments."
      : user.role === "patient"
        ? "Open today's plan and keep your care team updated."
        : "Access the tools available for your account role.";

  return <AppShell active="more">
    <BrandHeader title="Profile" subtitle="Your identity and workspace access." />
    <Card tone="blue">
      <StatusBadge label={roleLabel(user.role)} tone="blue" />
      <Body>{user.full_name || "Movena user"}</Body>
      <Body muted>{user.email}</Body>
    </Card>
    <View>
      <SectionTitle>Workspace</SectionTitle>
      <ActionRow title={workspaceTitle} detail={workspaceDetail} icon={administrator ? "shield-checkmark-outline" : therapist ? "people-outline" : user.role === "patient" ? "heart-outline" : "apps-outline"} onPress={() => router.replace(homeRoute(user.role) as never)} />
      {therapist || administrator ? <ActionRow title="Review queue" detail="Responses requiring clinical follow-up" icon="document-text-outline" onPress={() => router.push("/review")} /> : null}
      {user.role === "patient" ? <ActionRow title="Care team" detail="Therapists connected to your care" icon="people-circle-outline" onPress={() => router.push("/care-team")} /> : null}
    </View>
    <PrimaryButton title="Log out" secondary onPress={async () => { await signOut(); router.replace("/"); }} />
  </AppShell>;
}
