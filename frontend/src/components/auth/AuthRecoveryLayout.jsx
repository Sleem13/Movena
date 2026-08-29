import { ArrowLeft } from "lucide-react";

import { Card } from "../common/UI.jsx";

export default function AuthRecoveryLayout({ children, onLogin }) {
  return (
    <main className="mx-auto w-full max-w-lg px-6 py-12">
      <button
        onClick={onLogin}
        className="mb-6 inline-flex items-center gap-2 text-sm font-semibold text-slate-500 hover:text-clinical-blue"
      >
        <ArrowLeft size={16} />
        Back to login
      </button>
      <Card className="p-6 sm:p-8">{children}</Card>
    </main>
  );
}
