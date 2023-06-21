#!/usr/bin/env python
# *_* coding: utf-8 *_*

"""
generate the pages for kevingoldsmith.com
"""

__version__ = "2.0.0"
__author__ = "Kevin Goldsmith"
__copyright__ = "Copyright 2021, Kevin Goldsmith"
__license__ = "MIT"
__status__ = "Production"  # Prototype, Development or Production

import argparse
import logging
import os

import jinja2  # type: ignore
from xmlrpc.client import boolean

import generate_resume_page
import generate_writing_page
import generate_talk_pages
import generate_photo_pages
import generate_contact_pages
from common import get_output_directory, initialize_logging


def generate_other_pages(debug_mode: boolean = False) -> None:
    """generate the simpler pages"""
    other_pages = [
        ("index.html", "site-index-template.html"),
        ("music.html", "music-template.html"),
        ("photography.html", "photography-template.html"),
    ]
    env = jinja2.Environment(loader=jinja2.FileSystemLoader("templates"))

    for page in other_pages:
        template = env.get_template(page[1])
        page_data = dict(debug_mode=debug_mode)
        output_path = os.path.join(get_output_directory(debug_mode), page[0])
        logger.info(f"writing: {output_path}")
        with open(output_path, "w") as file:
            file.write(template.render(page_data))


def main(debug_mode: boolean = False) -> None:
    """call the methods in the other modules"""
    generate_writing_page.generate_writing_page(
        debug_mode=debug_mode, output_file="writing.html"
    )
    generate_talk_pages.generate_conference_pages(debug_mode=debug_mode)
    generate_resume_page.generate_resume_page(
        debug_mode=debug_mode, output_file="resume.html"
    )
    generate_photo_pages.generate_photo_pages(debug_mode)
    generate_other_pages(debug_mode)
    generate_contact_pages.generate_contact_pages(debug_mode)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="generate the files for the site")
    parser.add_argument("--debug", action="store_true")
    args = parser.parse_args()
    logger = logging.getLogger(__name__)
    initialize_logging(logging.INFO)

    main(debug_mode=args.debug)
else:
    logger = logging.getLogger()
