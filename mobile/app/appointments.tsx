import { useCallback, useMemo, useState } from "react";
import { Linking } from "react-native";
import { AppShell, BrandHeader } from "@/src/components/AppShell";
import {
  Body,
  Card,
  EmptyState,
  ErrorState,
  Heading,
  Loading,
  PrimaryButton,
  StatusBadge,
} from "@/src/components/UI";
import {
  getAppointments,
  getTherapistAppointments,
  joinAppointment,
  type Appointment,
} from "@/src/api/care";
import { useAuth } from "@/src/context/AuthContext";
import { CareAccess } from "@/src/components/CareUI";
import { isTherapist } from "@/src/utils/care";
import { useCareResource } from "@/src/hooks/useCareResource";

export default function AppointmentsScreen() {
  return <CareAccess active="appointments"><AppointmentsContent /></CareAccess>;
}
function AppointmentsContent() {
  const { user } = useAuth();
  const therapist = isTherapist(user?.role);
  const fetchAppointments = useCallback(() => therapist ? getTherapistAppointments() : getAppointments(), [therapist]);
  const { data, loading: busy, error, reload } = useCareResource(fetchAppointments);
  const rows = data ?? [];
  const [joiningId, setJoiningId] = useState("");
  const [joinError, setJoinError] = useState("");
  const { upcoming, past } = useMemo(() => {
    const now = Date.now();
    return {
      upcoming: rows.filter((row) => new Date(row.ends_at).getTime() >= now).sort((a, b) => new Date(a.starts_at).getTime() - new Date(b.starts_at).getTime()),
      past: rows.filter((row) => new Date(row.ends_at).getTime() < now).sort((a, b) => new Date(b.starts_at).getTime() - new Date(a.starts_at).getTime()),
    };
  }, [rows]);
  const join = async (row: Appointment) => {
    try { setJoiningId(row.appointment_id); setJoinError("");
      const data = await joinAppointment(row.appointment_id);
      await Linking.openURL(
        `${data.room_url}?t=${encodeURIComponent(data.meeting_token)}`,
      );
    } catch (e) {
      setJoinError(e instanceof Error ? e.message : "Could not join this appointment.");
    } finally { setJoiningId(""); }
  };
  return (
    <AppShell active="appointments">
      <BrandHeader
        title="Appointments"
        subtitle={therapist ? "Your patient schedule in device time." : "Times are shown in your device timezone."}
      />
      {busy ? <Loading /> : null}
      {error ? <ErrorState message={error} action={<PrimaryButton title="Try again" onPress={reload} />} /> : null}
      {joinError ? <ErrorState message={joinError} /> : null}
      {!busy && !error && !rows.length ? (
        <EmptyState
          title="No appointments"
          message="Your confirmed sessions will appear here."
        />
      ) : (
        <><Heading>Upcoming</Heading>{upcoming.length ? upcoming.map((row) => (
          <Card key={row.appointment_id}>
            <StatusBadge
              label={row.status}
              tone={row.status === "confirmed" ? "success" : "blue"}
            />
            <Heading>{new Date(row.starts_at).toLocaleString()}</Heading>
            <Body muted>
              {therapist ? "Patient appointment · " : ""}{row.delivery_mode === "video"
                ? "Private video session · not recorded"
                : "In-person session"}
            </Body>
            {row.delivery_mode === "video" &&
            ["scheduled", "confirmed"].includes(row.status) ? (
              <PrimaryButton
                title={joiningId === row.appointment_id ? "Opening secure call…" : row.can_join ? "Join secure call" : "Available near appointment time"}
                disabled={!row.can_join || Boolean(joiningId)}
                onPress={() => join(row)}
              />
            ) : null}
          </Card>
        )) : <EmptyState title="No upcoming appointments" message="Your next confirmed session will appear here." />}
        {past.length ? <><Heading>Past</Heading>{past.map((row) => <Card key={row.appointment_id}><StatusBadge label={row.status} tone="muted" /><Heading>{new Date(row.starts_at).toLocaleString()}</Heading><Body muted>{row.delivery_mode === "video" ? "Private video session" : "In-person session"}</Body></Card>)}</> : null}</>
      )}
    </AppShell>
  );
}
