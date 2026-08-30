# PhysioVision branding system

## Source of truth

`frontend/public/brand-wordmark.png` is the approved master artwork. Generated icons are deterministic crops and resizes of that file; they must not be independently redrawn. Product copy, color tokens, and web asset paths live in `frontend/src/config/brand.js`. The Expo client mirrors the same contract in `mobile/src/config/brand.ts` because native bundlers require static asset references.

## Web assets

| Asset | Use |
|---|---|
| `icons/favicon-16.png`, `icons/favicon-32.png` | Browser tabs and bookmarks |
| `icons/apple-touch-icon.png` | iOS home screen |
| `icons/icon-192.png`, `icons/icon-512.png` | Web-app manifest and installed PWA |
| `brand-wordmark-420.webp`, `brand-wordmark-840.webp` | Optimized responsive headers and authentication screens |
| `brand-wordmark-420.png`, `brand-wordmark-840.png` | PNG fallbacks |
| `manifest.webmanifest` | Installed-web-app metadata |

The optimized 420-pixel WebP is about 19 KB, compared with roughly 600 KB for the master artwork. `BrandLogo` declares intrinsic dimensions and a WebP `srcset`, preventing layout shift while retaining a PNG fallback.

```powershell
.\.venv\Scripts\python.exe scripts\generate_brand_assets.py
```

## Mobile assets

Expo uses the same approved mark for the application icon, Android adaptive foreground, splash image, and web favicon. The adaptive foreground is centered inside the Android safe zone so launchers can apply their own mask without clipping the mark. The mobile wordmark is an optimized PNG rather than the full master file.

```powershell
.\.venv\Scripts\python.exe mobile\scripts\generate_brand_assets.py
```

After changing the approved master, run both generators, inspect the 16-pixel favicon, Apple icon, masked Android icon, splash screen, light/dark browser chrome, and installed PWA. Do not substitute a condition-specific or runner-only symbol for the approved PhysioVision mark.

## Release check

- Browser favicon, login header, authenticated header, Expo header, splash, and installed icons use the same mark.
- Manifest name, theme color, and icon sizes pass the browser application audit.
- Wordmarks remain readable at 200% zoom and do not contain text below the intended display size.
- Asset changes are reviewed visually on Chrome, Safari/iOS, and Android before release.
