---
title: "fix: publish desktop release installers"
date: 2026-11-25
branch: fix/release-installers
request-source: "project chat, 2026-11-25"
---

## Request

Supply the missing macOS DMG and Windows EXE for v0.1.0 and package them for future releases, following the platform targets used by SOS My Language.

## Changes

- Build an Apple Silicon disk image with the existing local macOS launcher's bundle identifier and WebKit origin to preserve saved subscriptions.
- Build a per-user x64 Windows installer with a Start menu shortcut. The shortcut opens the reader in the default browser and keeps its local server in a console window.
- Bundle standalone Python and the built frontend on each platform. Build both installers on native pull request runners and require them for tag publication alongside the existing ZIP.
- Document installation in both READMEs. Use the installer build artifacts to backfill the existing release without moving its tag.

## Verification

- Confirmed that the published v0.1.0 initially contained only the runnable ZIP.
- Ran the backend unit suite and the frontend clean install, type check, and production build.
- Added a packaging smoke test that starts the bundled interpreter and reads the local UI. It failed before the desktop entry point existed.
- The native workflow verifies the macOS app signature and disk image, silently installs the Windows EXE, and checks the reader from each bundle.
