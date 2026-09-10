import { useEffect, useState } from "react";
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

export default function AppointmentsScreen() {
  return <CareAccess active="appointments"><AppointmentsContent /></CareAccess>;
}
function AppointmentsContent() {
  const { user } = useAuth();
  const therapist = isTherapist(user?.role);
  const [rows, setRows] = useState<Appointment[]>([]);
  const [busy, setBusy] = useState(true);
  const [error, setError] = useState("");
  useEffect(() => {
    (therapist ? getTherapistAppointments() : getAppointments())
      .then(setRows)
      .catch((e) => setError(e instanceof Error ? e.message : "Could not load appointments."))
      .finally(() => setBusy(false));
  }, [therapist]);
  const join = async (row: Appointment) => {
    try {
      const data = await joinAppointment(row.appointment_id);
      await Linking.openURL(
        `${data.room_url}?t=${encodeURIComponent(data.meeting_token)}`,
      );
    } catch (e) {
      setError(e instanceof Error ? e.message : "Could not join this appointment.");
    }
  };
  return (
    <AppShell active="appointments">
      <BrandHeader
        title="Appointments"
        subtitle={therapist ? "Your patient schedule in device time." : "Times are shown in your device timezone."}
      />
      {busy ? <Loading /> : null}
      {error ? <ErrorState message={error} /> : null}
      {!busy && !error && !rows.length ? (
        <EmptyState
          title="No appointments"
          message="Your confirmed sessions will appear here."
        />
      ) : (
        rows.map((row) => (
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
                title="Join secure call"
                disabled={!row.can_join}
                onPress={() => join(row)}
              />
            ) : null}
          </Card>
        ))
      )}
    </AppShell>
  );
}
