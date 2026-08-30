export const PAGE_PATHS = {
  home: "/",
  workspace: "/workspace",
  care: "/care",
  exercises: "/exercises",
  analyze: "/analyze",
  results: "/results",
  history: "/history",
  therapist: "/therapist",
  therapistPatients: "/therapist/patients",
  adminWorkflow: "/admin/workflow",
  adminUsers: "/admin/users",
  coach: "/coach",
  rehabPolicy: "/rehab-policy",
  about: "/about",
  login: "/login",
  register: "/register",
  forgotPassword: "/forgot-password",
  resetPassword: "/reset-password",
  verifyEmail: "/verify-email",
  profile: "/profile",
};

export function pageForPath(path, realtimeCoachingEnabled) {
  if (path.startsWith("/therapist/patients")) return "therapistPatients";
  if (path.startsWith("/therapist")) return "therapist";
  if (path.startsWith("/admin/users")) return "adminUsers";
  if (path.startsWith("/admin")) return "adminWorkflow";
  if (path.startsWith("/coach")) {
    return realtimeCoachingEnabled ? "coach" : "home";
  }
  return (
    Object.entries(PAGE_PATHS).find(([, value]) => value === path)?.[0] ||
    "home"
  );
}

export function landingPageForRole(user) {
  if (user?.role === "patient") return "care";
  if (user?.role === "therapist") return "therapist";
  if (user?.role === "super_admin") return "adminWorkflow";
  return "workspace";
}
