import "@testing-library/jest-dom/vitest";
import { cleanup } from "@testing-library/react";
import { afterEach } from "vitest";

if (!globalThis.localStorage) {
  const store = new Map();
  Object.defineProperty(globalThis, "localStorage", {
    configurable: true,
    value: {
      clear: () => store.clear(),
      getItem: (key) => store.get(String(key)) ?? null,
      removeItem: (key) => store.delete(String(key)),
      setItem: (key, value) => store.set(String(key), String(value)),
    },
  });
}

if (!URL.createObjectURL) URL.createObjectURL = () => "blob:test-artifact";
if (!URL.revokeObjectURL) URL.revokeObjectURL = () => {};

afterEach(() => cleanup());
