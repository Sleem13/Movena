export function validDataRightsDetails(value) {
  return value.trim().length <= 2000;
}

export function newDataRightsKey() {
  return globalThis.crypto?.randomUUID?.() || `privacy-${Date.now()}-${Math.random()}`;
}
