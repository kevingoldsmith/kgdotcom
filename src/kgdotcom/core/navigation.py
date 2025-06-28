#!/usr/bin/env python
# *_* coding: utf-8 *_*

"""Functions for the navigation bar"""

__version__ = "2.0.0"
__author__ = "Kevin Goldsmith"
__copyright__ = "Copyright 2021, Kevin Goldsmith"
__license__ = "MIT"
__status__ = "Production"  # Prototype, Development or Production

# --------------------------------------------------------------------------------

import os
from xmlrpc.client import boolean

CANNONICAL_ROOT = "https://kevingoldsmith.com/"
DEBUG_ROOT = ""
PAGES = [
    ("resume.html", "technology leader"),
    ("talks/index.html", "speaker"),
    ("writing.html", "writer"),
    ("music.html", "musician"),
    ("photography.html", "photographer"),
]
FORMAT_NAV_LI = '<li><a href="{url}">{title}</a></li>'


def get_href_root(
    relative_url: str, debug: boolean = False, relative_to_talks: boolean = False
) -> str:
    """get the root for a link file"""
    if not debug:
        return os.path.join(CANNONICAL_ROOT, relative_url.replace("index.html", ""))
    if not relative_to_talks:
        return relative_url
    return os.path.join("../", relative_url)


def get_talk_root_for_talk(debug: boolean = False) -> str:
    """figure url for link to root of talks"""
    if debug:
        return "index.html"
    return os.path.join(CANNONICAL_ROOT, "talks/")


def get_talk_url(filename: str, debug: boolean = False) -> str:
    """get the URL for a talk"""
    if debug:
        return filename
    return os.path.join(CANNONICAL_ROOT, "talks/", filename)
