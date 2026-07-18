# Mobile Physical-Device Testing

## Connect a phone to FastAPI

From the repository root:

```powershell
cd backend
..\.venv\Scripts\python.exe -m uvicorn app.main:app --reload --host 0.0.0.0 --port 8010
```

Find the development computer's private LAN address with `ipconfig`. In `mobile/.env`, use:

```dotenv
EXPO_PUBLIC_API_BASE_URL=http://<LAN_IP>:8010
EXPO_PUBLIC_APP_ENV=development
```

Do not use `localhost` or `127.0.0.1` on a physical phone; those refer to the phone. Android Emulator may use `http://10.0.2.2:8010`. Keep phone and computer on the same Wi-Fi, allow Python/port 8010 through the private-network firewall, and test from the phone browser first:

- `http://<LAN_IP>:8010/health`
- `http://<LAN_IP>:8010/api/v1/exercises`

Native requests are not governed by browser CORS. Expo web origins must be explicitly listed in `CORS_ALLOWED_ORIGINS`; production must never use wildcard CORS.

## Troubleshooting

- Cannot connect: confirm Uvicorn uses `0.0.0.0`, the LAN IP is current, both devices share a non-isolated Wi-Fi, and the phone URLs work in its browser.
- Timeout/interruption: retry with a short file, disable battery/data restrictions for the development build, and inspect backend logs without recording tokens or file contents.
- Firewall: allow the Python executable or TCP 8010 only on the trusted private network.
- VPN/WARP: temporarily disable split-tunnel-blocking VPN/WARP on both devices; some clients block local subnets.
- CORS: relevant to Expo web only. Add the exact web origin rather than `*`.
- Camera/library denial: enable permissions in system settings and use the in-app retry action.

Use synthetic or non-identifiable test recordings only. Do not expose port 8010 to the public internet.
