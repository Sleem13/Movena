import { useCallback } from "react";
import { getCoachingDashboard } from "@/src/api/care";
import { AppShell, BrandHeader } from "@/src/components/AppShell";
import { CareAccess } from "@/src/components/CareUI";
import { Body, Card, EmptyState, ErrorState, Heading, Loading, PrimaryButton, StatusBadge } from "@/src/components/UI";
import { useCareResource } from "@/src/hooks/useCareResource";

export default function GoalsScreen() { return <CareAccess roles={["patient"]} active="progress"><GoalsContent /></CareAccess>; }
function GoalsContent() {
  const fetchGoals = useCallback(() => getCoachingDashboard(), []); const { data, loading, error, reload } = useCareResource(fetchGoals);
  return <AppShell active="progress"><BrandHeader title="Your goals" subtitle="The activities and routines that matter to your recovery." />{loading ? <Loading label="Loading goals" /> : error ? <ErrorState message={error} action={<PrimaryButton title="Try again" onPress={reload} />} /> : data?.goals.length ? data.goals.map((goal) => <Card key={goal.goal_id}><StatusBadge label={`${goal.progress_percent}% complete`} tone={goal.status === "completed" ? "success" : "blue"} /><Heading>{goal.title}</Heading><Body>{goal.specific_action}</Body><Body muted>{goal.measurement} · target {new Date(goal.target_date).toLocaleDateString()}</Body></Card>) : <EmptyState title="No goals yet" message="Your agreed recovery goals will appear here." />}</AppShell>;
}
