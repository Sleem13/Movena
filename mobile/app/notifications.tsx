import { useEffect, useState } from "react";
import { AppShell, BrandHeader } from "@/src/components/AppShell";
import {
  Body,
  Card,
  EmptyState,
  ErrorState,
  Heading,
  Loading,
  StatusBadge,
} from "@/src/components/UI";
import { getNotifications, type CareNotification } from "@/src/api/care";
import { friendlyErrorMessage } from "@/src/api/client";
export default function NotificationsScreen() {
  const [rows, setRows] = useState<CareNotification[]>([]);
  const [busy, setBusy] = useState(true);
  const [error, setError] = useState("");
  useEffect(() => {
    getNotifications()
      .then(setRows)
      .catch((e) => setError(friendlyErrorMessage(e)))
      .finally(() => setBusy(false));
  }, []);
  return (
    <AppShell active="more">
      <BrandHeader
        title="Notifications"
        subtitle="Care, appointment, and account updates."
      />
      {busy ? <Loading /> : null}
      {error ? <ErrorState message={error} /> : null}
      {!busy && !rows.length ? (
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
          </Card>
        ))
      )}
    </AppShell>
  );
}
