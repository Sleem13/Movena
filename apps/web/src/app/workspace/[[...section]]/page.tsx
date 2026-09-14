import { Workspace } from "../../../components/Workspace";
export default async function Page({
  params,
}: {
  params: Promise<{ section?: string[] }>;
}) {
  const { section } = await params;
  return <Workspace section={section || []} />;
}
