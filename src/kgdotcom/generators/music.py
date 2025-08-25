#!/usr/bin/env python
# *_* coding: utf-8 *_*

"""
create the music.html page for my website with a list of musical releases and projects
"""

import argparse
import json
import logging
import os
from typing import Any, Dict
from xmlrpc.client import boolean

import jinja2  # type: ignore

from kgdotcom.core.common import (
    get_output_directory,
    initialize_logging,
)


def generate_music_page(
    debug_mode: boolean = True, output_file: str = "music.html"
) -> None:
    """from the music.json file, create the music.html file"""
    with open("data/music.json", encoding="utf-8") as file:
        music_data: Dict[str, Any] = json.load(file)

    # get the page template
    env = jinja2.Environment(loader=jinja2.FileSystemLoader("templates"))
    music_page_template = env.get_template("music-template.html")

    output_directory = get_output_directory(debug_mode)

    template_context = {
        "debug_mode": debug_mode,
        "music": music_data,
    }
    
    output_path = os.path.join(output_directory, output_file)
    logger.info("writing: %s", output_path)
    with open(output_path, "w", encoding="utf-8") as file:
        file.write(music_page_template.render(template_context))


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="generate the music file")
    parser.add_argument("--debug", action="store_true")
    args = parser.parse_args()
    logger = logging.getLogger(__name__)
    initialize_logging(logging.INFO)

    generate_music_page(debug_mode=args.debug)
else:
    logger = logging.getLogger()