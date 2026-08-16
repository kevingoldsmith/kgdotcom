# kgdotcom

Static site generator for [kevingoldsmith.com](https://kevingoldsmith.com) —
Kevin Goldsmith's personal website.

Content lives as structured JSON in `data/` (plus a `photos/` image tree).
Specialized Python generators read that content and render HTML with Jinja2
templates from `templates/`.

## Requirements

- Python 3.x (developed against 3.13)
- `make`

## Setup

```bash
make setup      # create the virtualenv and install dependencies (alias: make venv)
```

## Building

```bash
make build      # production build -> output/  (also generates the sitemap)
make debug      # debug build -> testoutput/  (debug flags on, opens in a browser)
make clean      # remove output directories
```

Builds are **incremental**: `kgdotcom.cli` only regenerates pages whose inputs
changed (see `needs_rebuild` in `src/kgdotcom/core/common.py`). A page's inputs
include its data files, its template, and every partial that template
`{% include %}`s, resolved recursively — so editing a shared partial such as
`templates/fonts.html` correctly rebuilds all the pages using it. Force a full
rebuild with the `--force` flag:

```bash
python -m kgdotcom.cli --debug --force
```

## Code quality & security

```bash
make lint       # pylint
make black      # format with black
make mypy       # strict type checking
make test       # unittest suite (tests/)
make scan       # bandit + pip-audit security scans
```

## Regression checkpoints (optional)

A golden-master workflow for confirming refactors don't change generated
output. Snapshot a known-good build, then diff a later build against it:

```bash
make checkpoint          # snapshot output/      -> lkgoutput/
make checkpoint-debug    # snapshot testoutput/  -> lkgtestoutput/
make testcheckpoint      # diff output/      vs lkgoutput/
make testdebugcheckpoint # diff testoutput/  vs lkgtestoutput/
```

The comparison (`tests/compare_outputs.py`) reports added/removed files and
per-file content diffs, exiting non-zero if the trees differ.

## Publishing

```bash
SCP_DEST=user@host:/path/to/webroot make publish   # deploy output/ via scripts/publish.sh
```

`SCP_DEST` is required — it isn't stored in the repo, which is public — and
`publish.sh` exits rather than run without it.

`.htaccess` is **not** uploaded by `make publish`, because `scp`'s glob skips
dotfiles. The server's copy is maintained by hand; `public/.htaccess` is kept in
sync so that copying `output/` with invisible files shown can't silently revert
it.

## Architecture

`src/kgdotcom/cli.py` orchestrates the build, dispatching to generators in
`src/kgdotcom/generators/`:

| Generator | Output | Source data |
|-----------|--------|-------------|
| `resume.py` | `resume.html` | `data/resume.json` |
| `writing.py` | `writing.html` | `data/writing.json` |
| `music.py` | `music.html` | `data/music.json` |
| `talks.py` | `talks/` index | `data/current_talks.json`, `data/conferences.json` |
| `talk_page.py` | individual talk pages | (called by `talks.py`) |
| `contact.py` | `contact/` pages + QR codes | `data/contact_me.json` |
| `photos.py` | `photos/` galleries | the `photos/` image tree |
| `sitemap.py` | `sitemap.xml` | the generated HTML |

`cli.py` also renders the simpler standalone pages (`index.html`,
`photography.html`). Shared helpers live in `src/kgdotcom/core/` (e.g.
`common.py` for output paths, JSON loading, logging, and rebuild checks;
`metadata.py` for structured page metadata; `navigation.py` for nav URLs) and
`src/kgdotcom/utils/` (EXIF, talk types).

### Page metadata

Every generated page renders `templates/metadata.html` — title, description,
canonical URL, Open Graph, Twitter card, and schema.org JSON-LD — from a
`PageMetadata` built by `core/metadata.py` for that page's type. Adding a page
type means adding a builder there and registering it in
`generate_page_metadata()`. The contact pages are deliberately `noindex` and are
excluded.

### Entry points

- `python -m kgdotcom.cli [--debug] [--force]` — full site generation
- `python -m kgdotcom.generators.sitemap` — standalone sitemap
- `kgdotcom-generate` — installed console script (= `kgdotcom.cli:main`)

## Content data

All textual content is structured JSON in `data/`:

| File | Contents |
|------|----------|
| `resume.json` | professional experience and skills |
| `writing.json` | articles, posts, publications |
| `music.json` | musical releases and projects |
| `current_talks.json` | speaking engagements / presentations |
| `conferences.json` | conference speaking history |
| `interviews.json` | media appearances |
| `contact_me.json` | contact info and social links |
| `common_meta.json`, `pagevariables.json` | shared page metadata / template variables |

## Photo galleries

`photos.py` walks the `photos/` tree: each subdirectory becomes a gallery
(with a grid page) and each image gets its own page.

**Image files** are named `YYYYMMDD-<name>.ext` (date prefix required for new
photos). Images sort **newest-first**, and the per-image prev/next navigation
follows that same order.

**Per-image sidecar** — an optional `<image>.json` next to the photo overrides
metadata used on the image page and grid caption:

```json
{ "title": "Long Beach, Washington", "description": "..." }
```

Title precedence is: sidecar `title` → embedded IPTC title → filename.

**Per-gallery sidecar** — an optional `<DirName>.json` in a gallery directory
sets the gallery's display name/description and optionally picks the cover
image by **filename** (default cover is the newest image):

```json
{ "name": "Czech Republic", "preview": "20240611-DSCF0705.jpg" }
```

## Dependencies

Key libraries: Jinja2 (templating), Pillow (image processing), qrcode (contact
QR codes), Markdown, requests / requests-cache (fetching cached web content),
pycountry (location formatting). Dev tooling: black, mypy, pylint, bandit,
pip-audit. Pages are built with SEO/structured metadata in mind.
