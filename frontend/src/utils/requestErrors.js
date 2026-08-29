export function getApiErrorMessage(error, fallback) {
  return error.response?.data?.message || fallback;
}
