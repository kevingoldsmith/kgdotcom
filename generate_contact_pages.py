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
import qrcode

import common

from datetime import datetime
from PIL import Image, ImageDraw, ImageFont


logger = logging.getLogger()


def generate_card_file(
    data: dict, output_directory: str, debug_mode: bool = False
) -> str:
    """
    generate_card_file _summary_

    Args:
        data (dict): _description_
        output_directory(str): the output path
        debug_mode (bool, optional): _description_. Defaults to False.

    Returns:
        the name of the generated card file
    """
    logger.debug("generating %s", data["vcf_filename"])

    data["rev"] = datetime.utcnow().strftime("%Y%m%dT%H%M%SZ")
    if "card_photo" in data:
        with open(os.path.join("assets", data["card_photo"]), "rb") as image_file:
            image_data = image_file.read()
            base64_image = base64.b64encode(image_data)
            data["photo_b64"] = base64_image.decode("utf-8")

    # get the template
    env = jinja2.Environment(loader=jinja2.FileSystemLoader("templates"))
    pagetemplate = env.get_template("contactfile.vcf")

    output_path = os.path.join(output_directory, data["vcf_filename"])
    logger.info(f"writing: {output_path}")
    with open(output_path, "w") as file:
        file.write(pagetemplate.render(data))

    return data["vcf_filename"]


def generate_contact_page(
    data: dict, output_directory: str, card_file_path: str, debug_mode: bool = False
) -> str:
    """
    generate_contact_page _summary_

    Args:
        data (dict): _description_
        output_directory(str): the output path
        card_file_path (str): the path of the card file to link to
        debug_mode (bool, optional): _description_. Defaults to False.

    Returns:
        the name of the generated card page
    """
    data["card_file_path"] = card_file_path
    data["card_photo_path"] = os.path.join("..", "img", data["card_photo"])
    if "header_image" in data:
        data["header_image"] = os.path.join("..", "img", data["header_image"])
    logger.debug("generating %s", data["filename"])

    # get the template
    env = jinja2.Environment(loader=jinja2.FileSystemLoader("templates"))
    pagetemplate = env.get_template("contactpage.html")

    output_path = os.path.join(output_directory, data["filename"])
    logger.info(f"writing: {output_path}")
    with open(output_path, "w") as file:
        file.write(pagetemplate.render(data))

    return data["filename"]


def generate_contact_wallpaper(
    data: dict, card_page_url: str, output_directory: str, debug_mode: bool = False
) -> None:
    """
    generate_contact_wallpaper _summary_

    Args:
        data (dict): _description_
        card_page_url (str): _description_
        output_directory (str): _description_
        debug_mode (bool, optional): _description_. Defaults to False.
    """
    filename, fileextension = os.path.splitext(data["filename"])
    output_path = os.path.join(output_directory, filename + "_wallpaper.png")
    logger.info("generating %s", output_path)

    qr_img = qrcode.make(card_page_url).convert("RGBA")
    logger.debug(f"QR image size: {qr_img.size}, mode: {qr_img.mode}")
    # assuming qr_img is 410x410

    if "card_photo" in data:
        photo_image = Image.open(os.path.join("assets", data["card_photo"])).convert(
            "RGBA"
        )
    else:
        photo_image = Image.new("RGBA", (200, 200))
    logger.debug(f"Photo image size: {photo_image.size}, mode: {photo_image.mode}")

    template_file = os.path.join(
        "assets", data.get("wallpaper_template", "wallpaper_template.png")
    )
    image_template = Image.open(template_file).convert("RGBA")
    logger.debug(
        f"Template image size: {image_template.size}, mode: {image_template.mode}"
    )

    output_image = Image.new(
        "RGBA", image_template.size, image_template.getpixel((0, 0))
    )
    logger.debug(f"Output image size: {output_image.size}, mode: {output_image.mode}")

    output_image.paste(image_template, (0, 0))
    output_image.paste(qr_img, (335, 1440), qr_img)
    output_image.paste(photo_image, (70, 69), photo_image)

    draw = ImageDraw.Draw(output_image)
    text = f"{data['first_name']} {data['last_name']}"
    font = ImageFont.truetype("assets/RobotoSlab.ttf", 108)
    color = (0, 0, 0)

    # Position of the text
    position = (70, 350)

    # Add text to image
    draw.text(position, text, color, font=font)

    output_image.save(output_path)


def generate_contact_pages(debug_mode: bool = False) -> None:
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

    common_contact_data = contact_me_data["common"]
    output_directory = os.path.join(common.get_output_directory(debug_mode), "contact")
    if not os.path.exists(output_directory):
        os.makedirs(output_directory)

    for page in contact_me_data["contacts"]:
        merged_data = common_data.copy()
        merged_data.update(common_contact_data)
        merged_data.update(page)
        card_file = generate_card_file(merged_data, output_directory, debug_mode)
        card_page = generate_contact_page(
            merged_data, output_directory, card_file, debug_mode
        )
        card_page_url = os.path.join("https://kevingoldsmith.com/contact", card_page)
        generate_contact_wallpaper(
            merged_data, card_page_url, output_directory, debug_mode
        )


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="generate the contact me pages")
    parser.add_argument("--debug", action="store_true")
    args = parser.parse_args()
    logger = logging.getLogger(__name__)
    common.initialize_logging(logging.INFO)

    generate_contact_pages(debug_mode=args.debug)
