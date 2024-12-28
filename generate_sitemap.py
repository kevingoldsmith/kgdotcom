#!/usr/bin/env python3
# *_* coding: utf-8 *_*

"""create a sitemap from the generated HTML files"""

__version__ = "1.0.0"
__author__ = "Kevin Goldsmith"
__copyright__ = "Copyright 2021, Kevin Goldsmith"
__license__ = "MIT"
__status__ = "Production"  # Prototype, Development or Production

# --------------------------------------------------------------------------------

import argparse
import datetime
import logging
import os
from string import Template
from typing import Tuple

from xmlrpc.client import boolean

from navigation import get_href_root
from common import get_output_directory, initialize_logging


def generate_sitemap(debug_mode: boolean = False) -> None:
    """walks the output directory and adds html files to the sitemap.xml file"""
    format_url = "<url><loc>{url}</loc><lastmod>{date}</lastmod><changefreq>monthly</changefreq><priority>{priority}</priority></url>"

    ignore_files = ["403page.html", "404page.html", "nortonsw_8ae7e2e0-1022-0.html"]
    ignore_paths = ["contact"]
    important_files = [
        "https://kevingoldsmith.com/resume.html",
        "https://kevingoldsmith.com/writing.html",
        "https://kevingoldsmith.com/talks/",
        "https://kevingoldsmith.com/music.html",
        "https://kevingoldsmith.com/photos/",
    ]

    sitemap_files = []
    path = get_output_directory(debug_mode)
    for path, _, files in os.walk(path):
        if not os.path.split(path)[-1] in ignore_paths:
            for file in files:
                ext = os.path.splitext(file)[1]
                if (not file in ignore_files) and (ext == ".html"):
                    path_list = path.split(os.sep)
                    sitemap_files.append(
                        (
                            os.path.join(path, file),
                            get_href_root(
                                os.path.join(*path_list[1:], file), debug_mode
                            ),
                        )
                    )

    sitemap_entries = []
    for sfile in sitemap_files:
        priority = 0.3
        if sfile[1] in important_files:
            priority = 0.8
        sitemap_entries.append(
            format_url.format(
                url=sfile[1],
                date=datetime.datetime.fromtimestamp(
                    os.path.getmtime(sfile[0])
                ).strftime("%Y-%m-%d"),
                priority=priority,
            )
        )

    with open("templates/sitemap-template.xml") as template_file:
        template = Template(template_file.read())

    sitemap_dict = dict(urllist="\n".join(sitemap_entries))
    logging.info("writing: sitemap.xml")
    with open(get_output_directory(debug_mode) + "sitemap.xml", "w") as output_file:
        output_file.write(template.substitute(sitemap_dict))


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="generate the sitemap")
    parser.add_argument("--debug", action="store_true")
    args = parser.parse_args()
    logger = logging.getLogger(__name__)
    initialize_logging(logging.INFO)
    generate_sitemap(args.debug)
else:
    logger = logging.getLogger()
