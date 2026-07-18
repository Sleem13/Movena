type Listener = (message: string) => void;
const listeners = new Set<Listener>();

export function subscribeToSessionExpiry(listener: Listener) {
  listeners.add(listener);
  return () => { listeners.delete(listener); };
}

export function publishSessionExpiry(message: string) {
  listeners.forEach((listener) => listener(message));
}
