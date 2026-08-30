# Linux release

AppImage, deb, and rpm, GPG-signed.

```bash
uv run briefcase create linux
uv run briefcase package linux --target ubuntu
```

Sign with `gpg --detach-sign --armor`. Runtime libraries: `libegl1`, `libxcb-cursor0`, `libxkbcommon-x11-0`.
