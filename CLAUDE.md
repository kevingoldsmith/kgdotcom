# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

This is a Python-based static site generator for Kevin Goldsmith's personal website (kevingoldsmith.com). The architecture consists of specialized page generators that read structured JSON data and generate HTML pages using Jinja2 templates.

## Development Commands

### Setup
```bash
make setup      # Creates virtual environment and installs dependencies
make venv       # Alternative command for setup
```

### Building
```bash
make build      # Production build to output/
make debug      # Debug build to testoutput/
make clean      # Clean output directories
```

### Code Quality
```bash
make lint       # Run pylint on all Python files
make black      # Format code with black
make mypy       # Type checking with strict settings
make test       # Run test suite (using unittest discover)
make scan       # Security scanning with bandit and pip-audit
```

### Testing and Comparison
```bash
make checkpoint          # Create checkpoint from output/
make checkpoint-debug    # Create checkpoint from testoutput/
make testcheckpoint      # Compare output/ vs lkgoutput/
make testdebugcheckpoint # Compare testoutput/ vs lkgtestoutput/
```

### Publishing
```bash
make publish    # Deploy to production (via scripts/publish.sh)
```

### Photo Sync
```bash
make photos-pull   # Download new/changed photos from S3 (non-destructive)
make photos-push   # Mirror local photos/ up to S3 (run after adding photos)
```

## Architecture

### Core Generation Flow
The main orchestrator is `src/kgdotcom/cli.py` which calls specialized generators:

- **src/kgdotcom/generators/resume.py** - Processes `data/resume.json` into resume HTML
- **src/kgdotcom/generators/writing.py** - Converts `data/writing.json` into writing portfolio
- **src/kgdotcom/generators/music.py** - Builds `music.html` from `data/music.json` (musical releases and projects)
- **src/kgdotcom/generators/talks.py** - Creates conference/talk index pages from `data/current_talks.json`
- **src/kgdotcom/generators/talk_page.py** - Creates individual talk pages
- **src/kgdotcom/generators/photos.py** - Processes `photos/` directory for photo galleries with Gallery and Image classes
- **src/kgdotcom/generators/contact.py** - Dynamic contact pages with QR codes from `data/contact_me.json`
- **src/kgdotcom/generators/sitemap.py** - XML sitemap generation

`cli.py` also renders simpler standalone pages (`index.html`, `photography.html`) via `generate_other_pages()`. Builds are **incremental**: `main()` only regenerates pages whose inputs changed (`needs_rebuild` in `core/common.py`); pass `--force` to rebuild everything.

### Key Modules
- **src/kgdotcom/core/common.py** - Shared utilities including `get_output_directory()`, JSON loading, and logging setup
- **src/kgdotcom/core/navigation.py** - Navigation-related utilities
- **src/kgdotcom/utils/** - Utility modules for EXIF processing and talk types
- **scripts/build.sh** - Build orchestration with debug/production modes and asset copying

### Data Structure
All content is stored as structured JSON in `data/`:
- `resume.json` - Professional experience and skills
- `writing.json` - Articles, blog posts, and publications  
- `music.json` - Musical releases and projects
- `current_talks.json` - Speaking engagements and presentations
- `contact_me.json` - Contact information and social links
- `conferences.json` - Conference speaking history
- `interviews.json` - Media appearances
- `common_meta.json`, `pagevariables.json` - Shared page metadata and template variables

Photo content is not JSON: `photos.py` walks the `photos/` image tree directly (see Photo Galleries below).

### Photo Galleries
Each subdirectory of `photos/` becomes a gallery (grid page) and each image gets its own page.
- Image files are named `YYYYMMDD-<name>.ext` (date prefix required for new photos). Images sort **newest-first**, and per-image prev/next navigation follows that same order.
- Optional `<image>.json` sidecar overrides `title`/`description`. Title precedence: sidecar `title` → embedded IPTC title → filename.
- Optional `<DirName>.json` gallery sidecar sets the gallery `name`/`description` and may select the cover via `preview` (matched by image **filename**); the default cover is the newest image.

#### Photo Storage and Sync
`photos/` is **gitignored** — the repo is public, so photos live in a private S3 bucket instead and are synced across machines with rclone (not checked into git, not manually copied). `scripts/photos.sh` wraps both directions; `scripts/photos-filter.txt` excludes macOS cruft (`.DS_Store`, etc.) from the bucket.
- **pull** (`make photos-pull` / `scripts/photos.sh pull`) — non-destructive `rclone copy` from S3; brings in new/changed photos, never deletes local files.
- **push** (`make photos-push` / `scripts/photos.sh push`) — `rclone sync` local → S3, **including deletions**. Local is the source of truth, so only push from a machine whose `photos/` is current.
- `build.sh` runs **pull** automatically before generation (non-fatal if offline), so builds reflect the latest photos. Push is always manual to avoid a stale machine overwriting newer photos in the bucket.
- Bucket is configured in `scripts/photos.sh` (override with the `PHOTOS_REMOTE` env var); rclone needs an `s3` remote configured per machine.

### Template System
Jinja2 templates in `templates/` directory generate final HTML. Each generator loads appropriate templates and passes structured data for rendering.

### Build Modes
- **Production**: Outputs to `output/` directory, includes sitemap generation
- **Debug**: Outputs to `testoutput/` directory with debug flags enabled, auto-opens in browser

### CLI Entry Points
The project provides CLI access via:
- `python -m kgdotcom.cli [--debug] [--force]` - Main site generation (`--force` rebuilds all pages)
- `python -m kgdotcom.generators.sitemap` - Standalone sitemap generation
- `kgdotcom-generate` - Console script (after installation, = `kgdotcom.cli:main`)

## Dependencies

Key dependencies include:
- Jinja2 for templating
- Pillow for image processing  
- QRCode generation for contact pages
- Markdown processing for content
- requests and requests-cache for web content fetching
- pycountry for location formatting

### Development Dependencies
- Type checking with mypy and formatting with black
- pylint for linting
- unittest for testing framework
- bandit and pip-audit for security scanning
- all pages should be optimized for SEO including structured metadata for LLM parsing