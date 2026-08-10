import { Body, Card, Heading, SafetyNotice, Screen, StatusBadge, Title } from "@/src/components/UI";

export default function LimitationsScreen() {
  return <Screen>
    <StatusBadge label="Invite-only launch candidate · not public" tone="warning" />
    <Title>Known limitations</Title>
    <Card><Heading>Five exercises only</Heading><Body>Use only bodyweight squat, sit-to-stand, knee extension, shoulder abduction, or hip abduction, and select the movement manually.</Body></Card>
    <Card><Heading>Recording quality matters</Heading><Body>Camera angle, framing, lighting, clothing, occlusion, rapid motion, and network conditions can change or prevent a result. Pose landmarks and movement feedback may be inaccurate.</Body></Card>
    <Card><Heading>Rejected is not a clinical finding</Heading><Body>A rejected result means the recording or movement evidence was insufficient. Movement scores are engineering summaries, not clinical scores.</Body></Card>
    <Card tone="warning"><Heading>Not medical advice</Heading><Body>This beta is not a medical device and is not for diagnosis, treatment prescription, emergency use, or medical decisions. Rule-based analysis remains primary; recognition only suggests an exercise label and does not assess form.</Body></Card>
    <Card><Heading>Test data and support</Heading><Body>Use test videos only. Never upload real patients, identifiable personal information, or sensitive health information. Use the private feedback, issue, support, and deletion contacts supplied in your invitation.</Body></Card>
    <SafetyNotice />
  </Screen>;
}
