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

import os
import argparse
import jinja2
import generate_resume_page
import generate_writing_page
from common import get_output_directory


def generate_other_pages(debug_mode=False):
    """generate the simpler pages"""
    other_pages = [
        ('index.html', 'site-index-template.html'),
        ('music.html', 'music-template.html'),
        ('photography.html', 'photography-template.html')
    ]
    env = jinja2.Environment(loader=jinja2.FileSystemLoader('templates'))

    for page in other_pages:
        template = env.get_template(page[1])
        page_data = dict(debug_mode=debug_mode)
        output_path = os.path.join(get_output_directory(debug_mode), page[0])
        print('writing: ' + output_path)
        with open(output_path, 'w') as file:
            file.write(template.render(page_data))


def main(debug_mode=False):
    """call the methods in the other modules"""
    generate_writing_page.generate_writing_page(debug_mode=debug_mode,
        output_file='writing.html')
    generate_resume_page.generate_resume_page(debug_mode=debug_mode,
        output_file='resume.html')
    generate_other_pages(debug_mode)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='generate the writings file')
    parser.add_argument('--debug', action='store_true')
    args = parser.parse_args()

    main(debug_mode=args.debug)
