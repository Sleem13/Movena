import { useCallback, useState } from "react";
import { Alert, View } from "react-native";
import { useRouter } from "expo-router";
import { getConnections, getInvitations, invitePatient, respondToInvitation, type CareInvitation, type Connection } from "@/src/api/care";
import { AppShell, BrandHeader } from "@/src/components/AppShell";
import { CareAccess, Field, NavRow, careStyles } from "@/src/components/CareUI";
import { Body, Card, EmptyState, ErrorState, Heading, Loading, PrimaryButton, StatusBadge } from "@/src/components/UI";
import { useCareResource } from "@/src/hooks/useCareResource";
import { useAuth } from "@/src/context/AuthContext";
import { initials, isTherapist } from "@/src/utils/care";

type TeamData = { connections: Connection[]; invitations: CareInvitation[] };
export default function CareTeamScreen() { return <CareAccess active="team"><CareTeamContent /></CareAccess>; }
function CareTeamContent() {
  const router = useRouter();
  const { user } = useAuth(); const therapist = isTherapist(user?.role); const [email, setEmail] = useState(""); const [busy, setBusy] = useState(false);
  const fetchTeam = useCallback(async (): Promise<TeamData> => { const [connections, invitations] = await Promise.all([getConnections(), getInvitations()]); return { connections, invitations }; }, []);
  const { data, loading, error, reload } = useCareResource(fetchTeam);
  const respond = async (row: CareInvitation, action: "accept" | "decline") => { try { setBusy(true); await respondToInvitation(row.invitation_id, action); await reload(); } catch (cause) { Alert.alert("Could not update invitation", cause instanceof Error ? cause.message : "Please try again."); } finally { setBusy(false); } };
  const invite = async () => { if (!/^\S+@\S+\.\S+$/.test(email)) return Alert.alert("Enter a valid email", "Use the email address for your patient's verified Movena account."); try { setBusy(true); await invitePatient(email.trim()); setEmail(""); await reload(); } catch (cause) { Alert.alert("Could not send invitation", cause instanceof Error ? cause.message : "Please try again."); } finally { setBusy(false); } };
  const active = data?.connections.filter((row) => row.status === "active") || []; const pending = data?.invitations.filter((row) => row.status === "pending") || [];
  return <AppShell active="team"><BrandHeader title={therapist ? "Care connections" : "Your care team"} subtitle={therapist ? "Invite patients and manage active care relationships." : "See who can access your connected care records."} />
    {loading ? <Loading label="Loading care team" /> : error ? <ErrorState message={error} action={<PrimaryButton title="Try again" onPress={reload} />} /> : <>
      {therapist ? <Card tone="blue"><Heading>Invite a patient</Heading><Body muted>Use the email for their verified Movena account. Invitations expire after seven days.</Body><Field label="Patient email" autoCapitalize="none" keyboardType="email-address" value={email} onChangeText={setEmail} placeholder="patient@example.com" /><PrimaryButton title={busy ? "Sending…" : "Send invitation"} disabled={busy} onPress={invite} /></Card> : null}
      {pending.length ? <View style={careStyles.section}><Heading>{therapist ? "Pending invitations" : "Invitations"}</Heading>{pending.map((row) => <Card key={row.invitation_id}><StatusBadge label="Pending" tone="warning" /><Heading>{therapist ? row.email : row.therapist_name}</Heading><Body muted>Expires {new Date(row.expires_at).toLocaleDateString()}</Body>{!therapist ? <View style={careStyles.section}><PrimaryButton title="Accept" disabled={busy} onPress={() => respond(row, "accept")} /><PrimaryButton title="Decline" secondary disabled={busy} onPress={() => respond(row, "decline")} /></View> : null}</Card>)}</View> : null}
      <View style={careStyles.section}><Heading>{therapist ? "Connected patients" : "Your therapists"}</Heading>{active.length ? active.map((row) => { const name = therapist ? row.patient_name : row.therapist_name; return <NavRow key={row.assignment_id} initials={initials(name)} title={name} detail={`Connected ${new Date(row.assigned_at).toLocaleDateString()}`} onPress={() => therapist ? router.push({ pathname: "/patient/[id]", params: { id: row.patient_id } }) : Alert.alert("Care connection", `${name} currently has access to your connected care records.`)} />; }) : <EmptyState title="No active connections" message={therapist ? "Invite a patient to connect their care account." : "A therapist invitation will appear here when available."} />}</View>
    </>}
  </AppShell>;
}
