import { useCallback, useState } from "react";
import { Alert } from "react-native";
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
import { getNotifications, markNotificationRead, type CareNotification } from "@/src/api/care";
import { CareAccess } from "@/src/components/CareUI";
import { useCareResource } from "@/src/hooks/useCareResource";
export default function NotificationsScreen() {
  return <CareAccess roles={["patient"]} active="more"><NotificationsContent /></CareAccess>;
}
function NotificationsContent() {
  const fetchRows = useCallback(() => getNotifications(), []);
  const { data, loading: busy, error, reload } = useCareResource<CareNotification[]>(fetchRows);
  const rows = data ?? [];
  const [updating, setUpdating] = useState("");
  const markRead = async (row: CareNotification) => {
    try { setUpdating(row.notification_id); await markNotificationRead(row.notification_id); await reload(); }
    catch (cause) { Alert.alert("Could not update notification", cause instanceof Error ? cause.message : "Please try again."); }
    finally { setUpdating(""); }
  };
  return (
    <AppShell active="more">
      <BrandHeader
        title="Notifications"
        subtitle="Care, appointment, and account updates."
      />
      {busy ? <Loading /> : null}
      {error ? <ErrorState message={error} action={<PrimaryButton title="Try again" onPress={reload} />} /> : null}
      {!busy && !error && !rows.length ? (
        <EmptyState
          title="All caught up"
          message="You do not have any notifications."
        />
      ) : (
        rows.map((row) => (
          <Card key={row.notification_id}>
            {!row.read_at ? <StatusBadge label="New" /> : null}
            <Heading>{row.title}</Heading>
            <Body>{row.body}</Body>
            <Body muted>{new Date(row.created_at).toLocaleString()}</Body>
            {!row.read_at ? <PrimaryButton title={updating === row.notification_id ? "Marking…" : "Mark as read"} secondary disabled={Boolean(updating)} onPress={() => markRead(row)} /> : null}
          </Card>
        ))
      )}
    </AppShell>
  );
}
