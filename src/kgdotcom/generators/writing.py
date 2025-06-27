#!/usr/bin/env python
# *_* coding: utf-8 *_*

"""
create the writing.html page for my website with a list of articles to read
"""

__version__ = "2.0.0"
__author__ = "Kevin Goldsmith"
__copyright__ = "Copyright 2021, Kevin Goldsmith"
__license__ = "MIT"
__status__ = "Production"  # Prototype, Development or Production

# --------------------------------------------------------------------------------

import argparse
import json
import logging
import os

import jinja2  # type: ignore
from xmlrpc.client import boolean

from kgdotcom.core.common import (
    get_output_directory,
    validate_url,
    format_month_day_year_from_string,
    initialize_logging,
)


def tagify_tag(tag: str) -> str:
    """make tags work for selection"""
    tag = tag.replace(" ", "-")
    return tag.lower()


def generate_writing_page(
    debug_mode: boolean = True, output_file: str = "writing.html"
) -> None:
    """from the writing.json file, create the writing.html file"""
    with open("data/writing.json") as file:
        writings = json.load(file)

    writings = sorted(writings, key=lambda k: k["date"], reverse=True)

    # get the page template
    env = jinja2.Environment(loader=jinja2.FileSystemLoader("templates"))
    writingpagetemplate = env.get_template("writing-template.html")

    article_list = []
    tag_set = set()
    for writing in writings:
        if len(writing["name"]) > 0:
            writing["formatteddate"] = format_month_day_year_from_string(
                writing["date"]
            )
            tag_list = []
            data_tag_list = []
            writing["tags"].sort()
            for tag in writing["tags"]:
                tag_set.add(tag)
                tag_list.append(tag)
                data_tag_list.append(tagify_tag(tag))
            writing["keywords"] = tag_list
            writing["datatags"] = data_tag_list
            validate_url(writing["url"])
            article_list.append(writing)

    button_list = []
    for tag in sorted(tag_set):
        button_list.append({"name": tag, "tag": tagify_tag(tag)})

    output_directory = get_output_directory(debug_mode)

    writings = dict(
        debug_mode=debug_mode, writinglist=article_list, tagbuttons=button_list
    )
    output_path = os.path.join(output_directory, output_file)
    logger.info(f"writing: {output_path}")
    with open(output_path, "w") as file:
        file.write(writingpagetemplate.render(writings))


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="generate the writings file")
    parser.add_argument("--debug", action="store_true")
    args = parser.parse_args()
    logger = logging.getLogger(__name__)
    initialize_logging(logging.INFO)

    generate_writing_page(debug_mode=args.debug, output_file="writing.html")
else:
    logger = logging.getLogger()
