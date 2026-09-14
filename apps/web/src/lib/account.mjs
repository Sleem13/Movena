export function validPassword(value) {
  return Array.from(value).length >= 8 && new TextEncoder().encode(value).length <= 72;
}
export function accountToken(search, hash) {
  const value = new URLSearchParams(hash.replace(/^#/, '')).get('token') || new URLSearchParams(search).get('token') || '';
  return value.length >= 32 && value.length <= 512 && !/\s/.test(value) ? value : '';
}
