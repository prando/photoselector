# PhotoSelector

Keyboard-first desktop culling for sessions of 500–3000 photos. Open a folder,
pick keepers, export a list (and optionally copy the files). Originals are never
modified.

This is a rewrite of the 2017 Tkinter script. The original lives at
[`legacy/photo_v0.py`](legacy/photo_v0.py). Architecture is in
[`docs/design.md`](docs/design.md). Milestone plans are in [`docs/plans/`](docs/plans/).

## Status

Culling workspace is in place: grid, loupe, compare, live picks, undo, text/copy
export, Drive protocol (disabled until `PHOTOSELECTOR_GOOGLE_CLIENT_ID` is set),
and packaging notes under `docs/release/`.

## Requirements

- Python 3.12+
- [uv](https://docs.astral.sh/uv/)
- On Linux, Qt needs: `libegl1`, `libxcb-cursor0`, `libxkbcommon-x11-0`

## Run

```bash
uv sync --extra dev
uv run python -m photoselector.main
```

On first launch you get the welcome screen. **Open folder** (or drop a directory)
scans JPEG, PNG, HEIC, and RAW files in the folder and one level of subfolders,
then writes `<folder>/.photoselector/catalog.db`.

```bash
uv run pytest
uv run ruff check src tests
uv run black --check src tests
uv run mypy src
```

## Output

Unchanged from v0: a list of picked photos, plus an optional copy. Export lands
in M05; M01 only builds the catalog those exports will read.

## Clone this enhancement

This work lives in the private Origin repo
`prasaanth-muralidharan/photoselectorenhancement`
([browse](https://cursor.com/codebase/prasaanth-muralidharan/photoselectorenhancement)).
Visibility is private; change it on that page if you want.

```bash
curl -fsSL https://downloads.cursor.com/origin/install.sh | sh
origin auth login
origin repo clone prasaanth-muralidharan/photoselectorenhancement
```

If `origin` is not found after install:

```bash
echo 'export PATH="$HOME/.local/bin:$PATH"' >> ~/.zshrc
source ~/.zshrc
```

Origin CLI docs: https://cursor.com/docs/origin/cli

To fold this into the 2017 GitHub repo after you have a local clone of
[prando/photoselector](https://github.com/prando/photoselector):

```bash
cd photoselector
git checkout -b modernize-qt
mkdir -p legacy
git mv photo.py legacy/photo_v0.py
git commit -m "Move Tkinter v0 app to legacy/photo_v0.py"
git remote add rewrite ../photoselectorenhancement
git fetch rewrite
git merge rewrite/main --allow-unrelated-histories
```
