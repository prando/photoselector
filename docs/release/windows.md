# Windows release

Per-user MSI (no admin) and a winget manifest.

```bash
uv run briefcase create windows
uv run briefcase package windows
```

Sign the MSI with Authenticode on a machine that holds the cert. Publish `manifests/p/PhotoSelector/PhotoSelector/<version>/` for winget. Do not commit `.pfx` files.
