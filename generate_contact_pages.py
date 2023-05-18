#!/usr/bin/env python3
# *_* coding: utf-8 *_*

"""
create the contact me pages for my website
"""

__version__ = "1.0.0"
__author__ = "Kevin Goldsmith"
__copyright__ = "Copyright 2023, Kevin Goldsmith"
__license__ = "MIT"
__status__ = "Development"  # Prototype, Development or Production

import argparse
import json
import logging
import os
from typing import List

import jinja2  # type: ignore

import common


logger = logging.getLogger()

def generate_contact_page(data:dict, debug_mode:bool = False) -> None:
    """
    generate_contact_page _summary_

    Args:
        data (dict): _description_
        debug_mode (bool, optional): _description_. Defaults to False.
    """
    pass

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="generate the contact me pages")
    parser.add_argument("--debug", action="store_true")
    args = parser.parse_args()
    logger = logging.getLogger(__name__)
    common.initialize_logging(logging.INFO)

    generate_contact_page(data={}, debug_mode=args.debug)
