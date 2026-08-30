# macOS release

Briefcase universal `.dmg` (arm64 + x86_64), Developer ID, notarized.

```bash
uv sync --extra dev
uv run briefcase create macOS
uv run briefcase build macOS
uv run briefcase package macOS --adhoc-sign   # local
# Production:
# codesign --deep --force --options runtime --sign "Developer ID Application: …" app
# xcrun notarytool submit PhotoSelector.dmg --keychain-profile "notary" --wait
# xcrun stapler staple PhotoSelector.dmg
```

Use minimal entitlements (no network client except Drive/version check). Do not commit certificates.
