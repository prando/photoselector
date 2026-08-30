# Legacy PhotoSelector (v0)

`photo_v0.py` is the original 2017 Tkinter/Pillow culling script, preserved
byte-for-byte from the upstream `photo.py` at the start of the rewrite.

It is **not** an entry point for the modern app. Run the Qt application with:

```bash
uv run python -m photoselector.main
```

v0 loaded a single directory of JPEG/GIF/BMP files, let you walk them one at a
time, mark keepers, then write `selected_photos.txt` and optionally copy files
with `shutil.copy`. The modern app keeps that output (a pick list and an
optional copy) and replaces the UI, catalog, and imaging pipeline.

Requires Python 2.7+ and Pillow if you still want to launch it:

```bash
python legacy/photo_v0.py
```
