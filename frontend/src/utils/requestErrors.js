export function getApiErrorMessage(error, fallback, messagesByCode = {}) {
  const code = error.response?.data?.error_code;
  return (
    (code && messagesByCode[code]) || error.response?.data?.message || fallback
  );
}
