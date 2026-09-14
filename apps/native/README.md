# Movena native replacement

Flutter Android and iOS client for the staged Movena rebuild. This is a development
preview of the connected recovery slice, not a signed replacement release.

See [BUILDING.md](BUILDING.md) for runtime configuration, signing requirements and
native verification gates. The legacy API is currently the authoritative writer,
accessed through Django `/api/v2`. No production data migration occurs at launch.

Source: `lib/core` contains API, session and preferences; `lib/features` contains
role workspaces and care/analysis journeys; `lib/generated` contains shared
contracts, translations and design tokens. Camera capture disables microphone
recording. Secure platform storage owns the bearer token.

Run `flutter analyze` and `flutter test`. Real-device camera, background/resume,
deep links, installation upgrades and release signing remain separate checks.
The full product cutover ledger is `../../docs/rebuild/STATUS.md`.
