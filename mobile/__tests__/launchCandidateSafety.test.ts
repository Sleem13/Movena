import fs from "node:fs";
import path from "node:path";
import { validateRemoteApiConfiguration } from "@/src/config/runtimeSafety";

describe("external beta launch-candidate safety", () => {
  it("fails closed when a remote build lacks a real HTTPS API", () => {
    expect(() => validateRemoteApiConfiguration("staging", undefined)).toThrow(/private HTTPS API URL/i);
    expect(() => validateRemoteApiConfiguration("staging", "http://staging.example.com")).toThrow(/HTTPS API URL/i);
    expect(() => validateRemoteApiConfiguration("production", "https://staging-api.example.invalid")).toThrow(/placeholder API URL/i);
  });

  it("allows local development and a real private HTTPS endpoint", () => {
    expect(() => validateRemoteApiConfiguration("development", "http://192.168.1.10:8010")).not.toThrow();
    expect(() => validateRemoteApiConfiguration("staging", "https://staging.example.com")).not.toThrow();
  });

  it("keeps limitations and beta boundaries visible", () => {
    const onboarding = fs.readFileSync(path.join(process.cwd(), "app/more.tsx"), "utf8");
    const limitations = fs.readFileSync(path.join(process.cwd(), "app/limitations.tsx"), "utf8");
    expect(onboarding).toContain("Invite-only beta launch candidate · not public");
    expect(onboarding).toContain("Known limitations");
    expect(limitations).toContain("Never upload real patients");
    expect(limitations).toContain("not for diagnosis, treatment prescription");
  });
});
