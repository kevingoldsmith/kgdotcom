# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

This is a Python-based static site generator for Kevin Goldsmith's personal website (kevingoldsmith.com). The architecture consists of specialized page generators that read structured JSON data and generate HTML pages using Jinja2 templates.

## Development Commands

### Setup
```bash
make setup  # Creates virtual environment and installs dependencies
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
make test       # Run test suite
```

### Publishing
```bash
make publish    # Deploy to production (via scripts/publish.sh)
```

## Architecture

### Core Generation Flow
The main orchestrator is `generate_site.py` which calls specialized generators:

- **generate_resume_page.py** - Processes `data/resume.json` into resume HTML
- **generate_writing_page.py** - Converts `data/writing.json` into writing portfolio
- **generate_talk_pages.py** - Creates individual and index pages from `data/current_talks.json`
- **generate_photo_pages.py** - Processes `photos/` directory for photo galleries
- **generate_contact_pages.py** - Dynamic contact pages with QR codes from `data/contact_me.json`
- **generate_sitemap.py** - XML sitemap generation

### Key Modules
- **common.py** - Shared utilities including `get_output_directory()`, JSON loading, and logging setup
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
- **Production**: Outputs to `output/` directory
- **Debug**: Outputs to `testoutput/` directory with debug flags enabled


## Dependencies

Key dependencies include:
- Jinja2 for templating
- Pillow for image processing  
- QRCode generation for contact pages
- Markdown processing for content
- Type checking with mypy and formatting with black