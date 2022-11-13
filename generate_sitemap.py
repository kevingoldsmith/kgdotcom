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
import os
import datetime
from string import Template
from xmlrpc.client import boolean
from navigation import get_href_root
from common import get_output_directory
from typing import Tuple


def generate_sitemap(debug_mode: boolean = False) -> None:
    """walks the output directory and adds html files to the sitemap.xml file"""
    format_url = "<url><loc>{url}</loc><lastmod>{date}</lastmod></url>"

    ignore_files = ["403page.html", "404page.html", "nortonsw_8ae7e2e0-1022-0.html"]

    sitemap_files = []
    path = get_output_directory(debug_mode)
    for path, _, files in os.walk(path):
        for file in files:
            ext = os.path.splitext(file)[1]
            if (not file in ignore_files) and (ext == ".html"):
                path_list = path.split(os.sep)
                # cheat since I know that there is only a single depth
                sitemap_files.append(
                    (
                        os.path.join(path, file),
                        get_href_root(os.path.join(path_list[1], file), debug_mode),
                    )
                )

    sitemap_entries = []
    for sfile in sitemap_files:
        sitemap_entries.append(
            format_url.format(
                url=sfile[1],
                date=datetime.datetime.fromtimestamp(
                    os.path.getmtime(sfile[0])
                ).strftime("%Y-%m-%d"),
            )
        )

    with open("templates/sitemap-template.xml") as template_file:
        template = Template(template_file.read())

    sitemap_dict = dict(urllist="\n".join(sitemap_entries))
    print("writing: sitemap.xml")
    with open(get_output_directory(debug_mode) + "sitemap.xml", "w") as output_file:
        output_file.write(template.substitute(sitemap_dict))


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="generate the sitemap")
    parser.add_argument("--debug", action="store_true")
    args = parser.parse_args()
    generate_sitemap(args.debug)
