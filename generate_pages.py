#!/usr/bin/env python
# *_* coding: utf-8 *_*

"""
generate the pages for kevingoldsmith.com
"""

__version__ = "2.0.0"
__author__ = "Kevin Goldsmith"
__copyright__ = "Copyright 2021, Kevin Goldsmith"
__license__ = "MIT"
__status__ = "Production"                               # Prototype, Development or Production

import argparse
import generate_resume_page_jinja
import generate_writing_page_jinja

def main(debug_mode=False):
    """call the methods in the other modules"""
    generate_writing_page_jinja.generate_writing_page(debug_mode=debug_mode,
        output_file='writing-jinja.html')
    generate_resume_page_jinja.generate_resume_page(debug_mode=debug_mode,
        output_file='resume-jinja.html')

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='generate the writings file')
    parser.add_argument('--debug', action='store_true')
    args = parser.parse_args()

    main(debug_mode=args.debug)
