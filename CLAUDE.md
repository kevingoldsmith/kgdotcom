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

## Architecture

### Core Generation Flow
The main orchestrator is `src/kgdotcom/cli.py` which calls specialized generators:

- **src/kgdotcom/generators/resume.py** - Processes `data/resume.json` into resume HTML
- **src/kgdotcom/generators/writing.py** - Converts `data/writing.json` into writing portfolio
- **src/kgdotcom/generators/talks.py** - Creates conference/talk index pages from `data/current_talks.json`
- **src/kgdotcom/generators/talk_page.py** - Creates individual talk pages
- **src/kgdotcom/generators/photos.py** - Processes `photos/` directory for photo galleries with Gallery and Image classes
- **src/kgdotcom/generators/contact.py** - Dynamic contact pages with QR codes from `data/contact_me.json`
- **src/kgdotcom/generators/sitemap.py** - XML sitemap generation

### Key Modules
- **src/kgdotcom/core/common.py** - Shared utilities including `get_output_directory()`, JSON loading, and logging setup
- **src/kgdotcom/core/navigation.py** - Navigation-related utilities
- **src/kgdotcom/utils/** - Utility modules for EXIF processing and talk types
- **scripts/build.sh** - Build orchestration with debug/production modes and asset copying

### Data Structure
All content is stored as structured JSON in `data/`:
- `resume.json` - Professional experience and skills
- `writing.json` - Articles, blog posts, and publications  
- `current_talks.json` - Speaking engagements and presentations
- `contact_me.json` - Contact information and social links
- `conferences.json` - Conference speaking history
- `interviews.json` - Media appearances

### Template System
Jinja2 templates in `templates/` directory generate final HTML. Each generator loads appropriate templates and passes structured data for rendering.

### Build Modes
- **Production**: Outputs to `output/` directory, includes sitemap generation
- **Debug**: Outputs to `testoutput/` directory with debug flags enabled, auto-opens in browser

### CLI Entry Points
The project provides CLI access via:
- `python -m kgdotcom.cli` - Main site generation
- `python -m kgdotcom.generators.sitemap` - Standalone sitemap generation
- `kgdotcom-generate` - Console script (after installation)

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