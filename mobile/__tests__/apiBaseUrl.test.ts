import { resolveApiBaseUrl } from "@/src/config/apiBaseUrl";

describe("mobile API base URL", () => {
  it("uses the local FastAPI port for Expo web on every development launch", () => {
    expect(resolveApiBaseUrl(undefined, "web")).toBe("http://127.0.0.1:8000");
  });

  it("keeps the Android emulator host alias and mobile backend port", () => {
    expect(resolveApiBaseUrl(undefined, "android")).toBe("http://10.0.2.2:8010");
  });

  it("prefers an explicit environment URL and removes its trailing slash", () => {
    expect(resolveApiBaseUrl(" https://api.example.com/ ", "web")).toBe("https://api.example.com");
  });
});
