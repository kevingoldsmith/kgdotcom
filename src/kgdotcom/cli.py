#!/usr/bin/env python
# *_* coding: utf-8 *_*

"""
generate the pages for kevingoldsmith.com
"""

import argparse
import logging
import os

from xmlrpc.client import boolean

import jinja2  # type: ignore

from kgdotcom.generators import resume, writing, talks, photos, contact, music
from kgdotcom.core.common import get_output_directory, initialize_logging, needs_rebuild


def generate_other_pages(debug_mode: boolean = False) -> None:
    """generate the simpler pages"""
    other_pages = [
        ("index.html", "site-index-template.html"),
        ("photography.html", "photography-template.html"),
    ]
    env = jinja2.Environment(loader=jinja2.FileSystemLoader("templates"))

    for page in other_pages:
        template = env.get_template(page[1])
        page_data = {"debug_mode": debug_mode}
        output_path = os.path.join(get_output_directory(debug_mode), page[0])
        logger.info("writing: %s", output_path)
        with open(output_path, "w", encoding="utf-8") as file:
            file.write(template.render(page_data))


def main(debug_mode: boolean = False, force_rebuild: boolean = False) -> None:
    """Generate only pages that need rebuilding"""
    generators = {
        "writing.html": lambda: writing.generate_writing_page(debug_mode=debug_mode, output_file="writing.html"),
        "music.html": lambda: music.generate_music_page(debug_mode=debug_mode, output_file="music.html"),
        "photos/": lambda: photos.generate_photo_pages(debug_mode),
        "contact/": lambda: contact.generate_contact_pages(debug_mode),
        "talks/": lambda: talks.generate_conference_pages(debug_mode=debug_mode),
        "resume.html": lambda: resume.generate_resume_page(debug_mode=debug_mode, output_file="resume.html"),
    }
    
    for page_key, generator_func in generators.items():
        if force_rebuild or needs_rebuild(page_key, debug_mode):
            logger.info("Rebuilding %s", page_key)
            generator_func()
        else:
            logger.info("Skipping %s - up to date", page_key)
    
    # Always generate other pages for now
    # TODO: Add dependency tracking for these
    generate_other_pages(debug_mode)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="generate the files for the site")
    parser.add_argument("--debug", action="store_true")
    parser.add_argument("--force", action="store_true", help="force rebuild of all pages")
    args = parser.parse_args()
    logger = logging.getLogger(__name__)
    initialize_logging(logging.INFO)

    main(debug_mode=args.debug, force_rebuild=args.force)
else:
    logger = logging.getLogger()
