import { StyleSheet, Text, View } from "react-native";
import { useRouter } from "expo-router";
import Constants from "expo-constants";

import { AppShell, BrandHeader } from "@/src/components/AppShell";
import { ActionRow, SectionTitle } from "@/src/components/GuidedUI";
import { colors } from "@/src/config/theme";
import { useAuth } from "@/src/context/AuthContext";
import { isTherapist } from "@/src/utils/care";

export default function MoreScreen() {
  const router = useRouter();
  const { user } = useAuth();
  const therapist = isTherapist(user?.role);
  const appVersion = Constants.expoConfig?.version ?? "0.29.0";
  return (
    <AppShell active="more">
      <BrandHeader
        title="Account"
        subtitle={user ? `${user.full_name || user.email} · ${therapist ? "Therapist" : user.role === "patient" ? "Patient" : "Team"} workspace` : "Account, support, and app information."}
      />
      <View style={styles.section}>
        <SectionTitle>Account</SectionTitle>
        <ActionRow
          title={user ? "Profile" : "Log in"}
          detail={user?.email || "Access protected session history"}
          icon="person-outline"
          onPress={() => router.push(user ? "/profile" : "/login")}
        />
      </View>
      {user && ["patient", "therapist"].includes(user.role) ? <View style={styles.section}>
        <SectionTitle>{therapist ? "Clinical workspace" : "Your care"}</SectionTitle>
        <ActionRow
          title={therapist ? "Connected patients" : "Today's plan"}
          detail={therapist ? "Plans, goals, and patient check-ins" : "Prescribed exercises and daily check-in"}
          icon={therapist ? "people-outline" : "calendar-outline"}
          onPress={() => router.push(therapist ? "/patients" : "/today" as never)}
        />
        {therapist ? <ActionRow title="Review queue" detail="Responses requiring clinical follow-up" icon="document-text-outline" onPress={() => router.push("/review")} /> : <ActionRow title="Recovery goals" detail="Progress toward what matters to you" icon="flag-outline" onPress={() => router.push("/goals")} />}
        <ActionRow title={therapist ? "Care connections" : "Your care team"} detail={therapist ? "Invite and connect patients" : "Therapists connected to your care"} icon="people-circle-outline" onPress={() => router.push("/care-team")} />
        {!therapist ? <><ActionRow
          title="Appointments"
          detail="Book and join private video sessions"
          icon="videocam-outline"
          onPress={() => router.push("/appointments" as never)}
        />
        <ActionRow
          title="Notifications"
          detail="Care and appointment updates"
          icon="notifications-outline"
          onPress={() => router.push("/notifications" as never)}
        />
        <ActionRow
          title="Care packages"
          detail="Pay securely in EGP"
          icon="card-outline"
          onPress={() => router.push("/billing" as never)}
        /></> : null}
      </View> : null}
      <View style={styles.section}>
        <SectionTitle>Help and settings</SectionTitle>
        <ActionRow
          title="Safety & privacy"
          detail="Recording guidance and data handling"
          icon="shield-checkmark-outline"
          onPress={() => router.push("/safety")}
        />
        <ActionRow
          title="Known limitations"
          detail="Understand what the analysis can and cannot do"
          icon="information-circle-outline"
          onPress={() => router.push("/limitations")}
        />
      </View>
      <View style={styles.about}>
        <Text style={styles.aboutTitle}>Movena</Text>
        <Text style={styles.aboutText}>
          Movement intelligence inside your rehabilitation journey.
        </Text>
        <Text style={styles.version}>Version {appVersion}</Text>
        <Text style={styles.version}>Invite-only beta launch candidate · not public</Text>
      </View>
    </AppShell>
  );
}

const styles = StyleSheet.create({
  section: { gap: 10 },
  about: {
    marginTop: 10,
    paddingVertical: 18,
    borderTopWidth: 1,
    borderTopColor: colors.border,
    gap: 4,
  },
  aboutTitle: { color: colors.text, fontSize: 17, fontWeight: "800" },
  aboutText: { color: colors.muted, fontSize: 13 },
  version: { color: colors.muted, fontSize: 12, marginTop: 5 },
});
