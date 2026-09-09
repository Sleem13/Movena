import { api } from "./api.js";

export const connectionsApi = {
  list: () => api.get("/api/v1/connections").then(({ data }) => data),
  invitations: () =>
    api.get("/api/v1/care-invitations").then(({ data }) => data),
  invite: (email) =>
    api.post("/api/v1/care-invitations", { email }).then(({ data }) => data),
  manage: (id, action) =>
    api
      .post(`/api/v1/care-invitations/${encodeURIComponent(id)}/${action}`)
      .then(({ data }) => data),
  respond: (id, action, token) =>
    api
      .post(`/api/v1/care-invitations/${encodeURIComponent(id)}/respond`, {
        action,
        token,
      })
      .then(({ data }) => data),
  lookup: (token) =>
    api
      .post("/api/v1/care-invitations/lookup", { token })
      .then(({ data }) => data),
  end: (id, reason) =>
    api
      .post(`/api/v1/connections/${encodeURIComponent(id)}/end`, { reason })
      .then(({ data }) => data),
  options: (q, unassigned) =>
    api
      .get("/api/v1/admin/assignment-options", { params: { q, unassigned } })
      .then(({ data }) => data),
  assign: (patient_id, therapist_user_id, reason) =>
    api
      .post("/api/v1/admin/assignments", {
        patient_id,
        therapist_user_id,
        reason,
      })
      .then(({ data }) => data),
};

const INVITATION_KEY = "movena_care_invitation";
export function pendingInvitation() {
  const hashToken = new URLSearchParams(window.location.hash.slice(1)).get(
    "invitation",
  );
  if (hashToken && hashToken.length <= 200) {
    sessionStorage.setItem(INVITATION_KEY, hashToken);
    window.history.replaceState(
      {},
      "",
      window.location.pathname + window.location.search,
    );
  }
  return sessionStorage.getItem(INVITATION_KEY);
}
export function clearInvitation() {
  sessionStorage.removeItem(INVITATION_KEY);
}
