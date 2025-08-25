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
from kgdotcom.core.common import get_output_directory, initialize_logging


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


def main(debug_mode: boolean = False) -> None:
    """call the methods in the other modules"""
    writing.generate_writing_page(debug_mode=debug_mode, output_file="writing.html")
    talks.generate_conference_pages(debug_mode=debug_mode)
    resume.generate_resume_page(debug_mode=debug_mode, output_file="resume.html")
    photos.generate_photo_pages(debug_mode)
    music.generate_music_page(debug_mode=debug_mode, output_file="music.html")
    generate_other_pages(debug_mode)
    contact.generate_contact_pages(debug_mode)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="generate the files for the site")
    parser.add_argument("--debug", action="store_true")
    args = parser.parse_args()
    logger = logging.getLogger(__name__)
    initialize_logging(logging.INFO)

    main(debug_mode=args.debug)
else:
    logger = logging.getLogger()
