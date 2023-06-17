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
import base64
import json
import logging
import os

import jinja2  # type: ignore

import common

from datetime import datetime


logger = logging.getLogger()

def generate_contact_page(data:dict, output_directory:str, debug_mode:bool = False) -> None:
    """
    generate_contact_page _summary_

    Args:
        data (dict): _description_
        debug_mode (bool, optional): _description_. Defaults to False.
    """
    print(data)
    logger.debug("generating %s", data['filename'])

    # get the template
    env = jinja2.Environment(loader=jinja2.FileSystemLoader("templates"))
    pagetemplate = env.get_template("contactpage.html")

    output_path = os.path.join(output_directory, data['filename'])
    logger.info(f"writing: {output_path}")
    with open(output_path, "w") as file:
        file.write(pagetemplate.render(data))


def generate_card_file(data:dict, output_directory:str, debug_mode:bool = False) -> None:
    """
    generate_card_file _summary_

    Args:
        data (dict): _description_
        output_directory(str): the output path
        debug_mode (bool, optional): _description_. Defaults to False.
    """
    logger.debug("generating %s", data['vcf_filename'])

    data['rev'] = datetime.utcnow().strftime("%Y%m%dT%H%M%SZ")
    if 'image' in data:
        with open(os.path.join('assets', data['image']), 'rb') as image_file:
            image_data = image_file.read()
            base64_image = base64.b64encode(image_data)
            data['photo_b64'] = base64_image.decode('utf-8')

    # get the template
    env = jinja2.Environment(loader=jinja2.FileSystemLoader("templates"))
    pagetemplate = env.get_template("contactfile.vcf")

    output_path = os.path.join(output_directory, data['vcf_filename'])
    logger.info(f"writing: {output_path}")
    with open(output_path, "w") as file:
        file.write(pagetemplate.render(data))


def generate_contact_pages(debug_mode:bool = False) -> None:
    """
    generate_contact_pages _summary_

    Args:
        debug_mode (bool, optional): _description_. Defaults to False.
    """
    # get the data file
    with open("data/contact_me.json", "r") as file:
        contact_me_data = json.load(file)

    with open("data/common_meta.json") as file:
        common_data = json.load(file)

    common_contact_data = contact_me_data['common']
    output_directory = os.path.join(common.get_output_directory(debug_mode), "contact")
    if not os.path.exists(output_directory):
        os.makedirs(output_directory)

    for page in contact_me_data['contacts']:
        merged_data = common_data.copy()
        merged_data.update(common_contact_data)
        merged_data.update(page)
        generate_contact_page(merged_data, output_directory, debug_mode)
        generate_card_file(merged_data, output_directory, debug_mode)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="generate the contact me pages")
    parser.add_argument("--debug", action="store_true")
    args = parser.parse_args()
    logger = logging.getLogger(__name__)
    common.initialize_logging(logging.INFO)

    generate_contact_pages(debug_mode=args.debug)
