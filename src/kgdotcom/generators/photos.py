#!/usr/bin/env python
# *_* coding: utf-8 *_*

"""
create the talks/ subdirectory of the website
"""

__version__ = "3.0.0"
__author__ = "Kevin Goldsmith"
__copyright__ = "Copyright 2022, Kevin Goldsmith"
__license__ = "MIT"
__status__ = "Development"  # Prototype, Development or Production

import argparse
import copy
import json
import logging
import os
from typing import Any, Tuple, List

import jinja2  # type: ignore
from PIL import Image as PILImage
from PIL import IptcImagePlugin

from kgdotcom.core import common
from kgdotcom.utils.exif import get_exif_data

__PHOTOS_DIRECTORY = "photos"
__SITE_URL = "https://kevingoldsmith.com/"


class Gallery: # pylint: disable=too-many-instance-attributes
    """
     A class representing a photo gallery.
    """
    def __init__(self, name: str, directory: str, parent: Any = None) -> None:
        self.name = name
        self.description = ""
        self.output_path = ""
        self.directory = directory
        self.sub_galleries = []
        self.images = []
        self.preview_image = None
        self.parent = parent

    def __str__(self) -> str:
        return (
            f"{self.name} / subgalleries: {self.sub_galleries} / images: {self.images}"
        )

    def __repr__(self) -> str:
        return str(self)

    def populate(self) -> None:
        """
        populate create the gallery from the directory
        This will create a list of images and sub-galleries.
        It will also set the preview image to the first image in the gallery.
        If the directory contains a JSON file with the same name as the gallery,
        it will load the metadata from that file.
        If the directory contains a subdirectory, it will create a new Gallery object
        for that subdirectory and populate it as well.
        If the directory contains no images or sub-galleries, it will not be added
        to the parent gallery's sub_galleries list.
        :return: None
        :rtype: None
        :raises: None
        :note: This method will modify the Gallery object in place.
        :note: This method will not return anything.
        :note: This method will not raise any exceptions.
        :note: This method will not create any files or directories.
        :note: This method will not modify any files or directories.
        """
        items = os.listdir(self.directory)
        for item in items:
            path = os.path.join(self.directory, item)
            if Image.is_image_file(path):
                self.images.append(Image(os.path.splitext(item)[0], path))
            elif os.path.isdir(path):
                newgal = Gallery(item, path, self)
                newgal.populate()
                if (len(newgal.images) > 0) or (len(newgal.sub_galleries) > 0):
                    self.sub_galleries.append(newgal)
        if len(self.images) > 0:
            self.preview_image = self.images[0]
        self.load_JSON_metadata()

    def load_JSON_metadata(self) -> None: # pylint: disable=invalid-name
        """
        load_JSON_metadata loads metadata from a JSON file
        with the same name as the gallery in the gallery's directory.
        If the file exists, it will read the JSON data and update the gallery's
        name, description, and preview image.
        :return: None
        :rtype: None
        :raises: None
        """
        json_file = os.path.join(self.directory, self.name + ".json")
        if os.path.exists(json_file):
            with open(json_file, "r", encoding="utf-8") as f:
                gallery_data = json.load(f)
                self.name = gallery_data.get("name", self.name)
                self.description = gallery_data.get("description", "")
                preview_name = gallery_data.get("preview")
                if preview_name:
                    list(
                        filter(lambda image: image["name"] == preview_name, self.images)
                    )


class Image: # pylint: disable=too-many-instance-attributes
    """ A class representing a photo image.
    It contains the name, path, image data, EXIF data, IPTC data,
    and any overrides from a JSON file with the same name as the image. """
    __GALLERY_PHOTO_MAX = (2000, 2000)
    __GALLERY_THUMB_MAX = (1000, 1000)

    def __init__(self, name: str, path: str) -> None:
        self.name = name
        self.path = path
        self.image = None
        self.exif = {}
        self.iptc = {}
        self.data_overrides = {}
        self.output_filename = ""
        self.output_file_path = ""
        self.thumb_filename = ""
        self.thumb_file_path = ""
        self.description = ""
        self.load_image()

    def __str__(self) -> str:
        return f"{self.name} - {self.path}"

    def __repr__(self) -> str:
        return str(self)

    def load_image(self) -> None:
        """
        load_image loads the image from the path and extracts EXIF and IPTC data.
        It also checks for a JSON file with the same name as the image
        to override the name and description."""
        self.image = PILImage.open(self.path)
        self.exif = get_exif_data(self.image)
        self.iptc = get_iptc_data(self.image)
        self.data_overrides = self.get_JSON_overrides()
        self.image.close()

    def get_JSON_overrides(self) -> dict: # pylint: disable=invalid-name
        """
        get_JSON_overrides reads a JSON file with the same name as the image

        Returns:
            dict: a dictionary with the overrides for the image
        """
        root_name = os.path.splitext(self.path)[0]
        json_file = root_name + ".json"
        overrides = {}
        if os.path.exists(json_file):
            with open(json_file, "r", encoding="utf-8") as f:
                overrides = json.load(f)
                self.name = overrides.get("name", self.name)
                self.description = overrides.get("description", "")
        return overrides

    def get_simple_metadata(self) -> dict:
        """
        get_simple_metadata returns a simplified version of the image metadata.

        Returns:
            dict: a dictionary with the simplified metadata
        """
        simple = {}
        simple["title"] = self.iptc.get("title", self.name)
        if "description" in self.iptc:
            simple["description"] = self.iptc["description"]
        exif_tags = [
            "Make",
            "Model",
            "LensModel",
            "FNumber",
            "FocalLength",
            "ExposureTime",
            "ISOSpeedRatings",
            "DateTimeOriginal",
            "GPSInfo",
        ]
        friendly_tags = {
            "LensModel": "Lens Model",
            "FNumber": "f-number",
            "FocalLength": "Focal Length",
            "ExposureTime": "Exposure Time",
            "ISOSpeedRatings": "ISO Speed",
            "DateTimeOriginal": "Capture Date",
            "GPSInfo": "GPS",
        }
        for tag in exif_tags:
            if tag in self.exif:
                friendly_tag = friendly_tags.get(tag, tag)
                simple[friendly_tag] = self.exif[tag]["processed"]
        if "GPS" in simple:
            if "simpleGPS" in simple["GPS"]:
                simple["GPS"] = simple["GPS"]["simpleGPS"]
            else:
                del simple["GPS"]
        override_tags = ["title", "description", "DateTimeOriginal"]
        for tag in override_tags:
            if tag in self.data_overrides:
                simple[tag] = self.data_overrides[tag]
        if (
            ("Make" in simple)
            and ("Model" in simple)
            and simple["Model"].startswith(simple["Make"])
        ):
            simple["Model"] = simple["Model"][len(simple["Make"]) + 1 :]

        return simple

    def generate_output_images(self, destination_path: str) -> None:
        """
        generate_output_images generates the output images for the gallery.

        Args:
            destination_path (str): the path to save the output images to
        """
        self.output_filename = os.path.basename(self.path)
        self.output_file_path = os.path.join(destination_path, self.output_filename)
        filename_split = os.path.splitext(self.output_filename)
        self.thumb_filename = f"{filename_split[0]}-thumb{filename_split[1]}"
        self.thumb_file_path = os.path.join(destination_path, self.thumb_filename)
        pil_image = PILImage.open(self.path)

        if not os.path.exists(self.output_file_path):
            new_image = pil_image.resize(
                Image.get_resized_image_dimensions(
                    pil_image.size, Image.__GALLERY_PHOTO_MAX
                ),
                resample=PILImage.Resampling.LANCZOS,
            )
            new_image.save(self.output_file_path)

        if not os.path.exists(self.thumb_file_path):
            new_thumbnail = pil_image.resize(
                Image.get_resized_image_dimensions(
                    pil_image.size, Image.__GALLERY_THUMB_MAX
                ),
                resample=PILImage.Resampling.LANCZOS,
            )
            new_thumbnail.save(self.thumb_file_path)

    @staticmethod
    def is_image_file(filename: str, extensions=None) -> bool:
        """
        is_image_file checks if a file is an image file based on its extension.

        Args:
            filename (str): _filename to check_
            extensions (_type_, optional): _list of extensions to check against_
            Defaults to None.

        Returns:
            bool: _True if the file is an image file, False otherwise_
        """
        if extensions is None:
            extensions = [".jpg", ".jpeg", ".gif", ".png"]
        return any(filename.endswith(e) for e in extensions)

    @staticmethod
    def get_resized_image_dimensions(
        orig_size: Tuple[int, int], max_size: Tuple[int, int]
    ) -> Tuple[int, int]:
        """
        get_resized_image_dimensions calculates the new dimensions for an image

        Args:
            orig_size (Tuple[int, int]): _original size of the image_
            max_size (Tuple[int, int]): _maximum size for the image_

        Returns:
            Tuple[int, int]: _new dimensions for the image_
        """
        if (orig_size[0] <= max_size[0]) and (orig_size[1] <= max_size[1]):
            return orig_size
        aspect_ratio = float(orig_size[0]) / float(orig_size[1])
        if aspect_ratio > 1.0:  # landscape
            return (int(max_size[0]), int(max_size[1] / aspect_ratio))
        return (int(max_size[0] * aspect_ratio), int(max_size[1]))


def get_prev_next_nextnext(
    image_list: List[Image], image: Image
) -> Tuple[Image, Image, Image]:
    """
    get_prev_next_nextnext returns the previous, next, and next-next images

    Args:
        image_list (List[Image]): _list of images in the gallery
        image (Image): _image to find the previous, next, and next-next images for_

    Returns:
        Tuple[Image, Image, Image]: _previous, next, and next-next images_
    """
    prev_el = None
    next_el = None
    next_next_el = None
    for index, elem in enumerate(image_list):
        if image.name == elem.name:
            if index - 1 >= 0:
                prev_el = image_list[index - 1]
            if index + 1 < len(image_list):
                next_el = image_list[index + 1]
            if index + 2 < len(image_list):
                next_next_el = image_list[index + 2]
            break
    return prev_el, next_el, next_next_el


def get_iptc_data(image: PILImage.Image) -> dict:
    """Return a dict with the raw IPTC data."""

    iptc_data = {}
    raw_iptc = {}

    # PILs IptcImagePlugin issues a SyntaxError in certain circumstances
    # with malformed metadata, see PIL/IptcImagePlugin.py", line 71.
    # ( https://github.com/python-pillow/Pillow/blob/
    # 9dd0348be2751beb2c617e32ff9985aa2f92ae5f/src/PIL/IptcImagePlugin.py#L71 )
    raw_iptc = IptcImagePlugin.getiptcinfo(image)

    # IPTC fields are catalogued in:
    # https://www.iptc.org/std/photometadata/specification/IPTC-PhotoMetadata
    # 2:05 is the IPTC title property
    if raw_iptc and (2, 5) in raw_iptc:
        iptc_data["title"] = raw_iptc[(2, 5)].decode("utf-8", errors="replace")

    # 2:120 is the IPTC description property
    if raw_iptc and (2, 120) in raw_iptc:
        iptc_data["description"] = raw_iptc[(2, 120)].decode("utf-8", errors="replace")

    # 2:105 is the IPTC headline property
    if raw_iptc and (2, 105) in raw_iptc:
        iptc_data["headline"] = raw_iptc[(2, 105)].decode("utf-8", errors="replace")

    return iptc_data


def create_image_page( # pylint: disable=too-many-locals
    gallery: Gallery, image: Image, path: str, root_path: str, debug_mode
) -> None:
    """create_image_page creates the image page for the given image in the given gallery
    :param gallery: the Gallery object that contains the image
    :param image: the Image object to create the page for
    :param path: the path to create the image page in
    :param root_path: the root path for the gallery
    :param debug_mode: whether to run in debug mode
    :return: None
    :rtype: None"""
    logger.info("creating image page for: %s at %s", image.output_filename, path)

    simple_metadata = image.get_simple_metadata()

    # get the page template
    env = jinja2.Environment(loader=jinja2.FileSystemLoader("templates"))
    gallery_page_template = env.get_template("photo-page-template.html")

    # get the page variables (which becomes our template dictionary)
    with open("data/pagevariables.json", encoding="utf-8") as file:
        pagevariables = json.load(file)

    # build breadcrumbs
    temp_gallery = gallery
    breadcrumbs = []
    relative_path = "index.html"
    while temp_gallery:
        breadcrumbs.append((temp_gallery.name, relative_path))
        temp_gallery = temp_gallery.parent
        relative_path = "../" + relative_path
    breadcrumbs.reverse()

    previous, next_image, next_next_image = get_prev_next_nextnext(gallery.images,
                                                                   image)
    image.image_page = image.name + ".html"
    image.image_page_path = os.path.join(path, image.name + ".html")

    pagevalues = copy.deepcopy(pagevariables)
    pagevalues["debug_mode"] = debug_mode
    pagevalues["title"] = f"{simple_metadata['title']}: a photo by Kevin Goldsmith"
    pagevalues["rootpath"] = root_path
    pagevalues["photo"] = image
    pagevalues["gallery"] = gallery
    pagevalues["metadata"] = simple_metadata
    pagevalues["breadcrumbs"] = breadcrumbs
    if "Capture Date" in simple_metadata:
        pagevalues["date_taken"] = simple_metadata["Capture Date"].strftime("%B %d, %Y")
        del simple_metadata["Capture Date"]
    pagevalues["previous_image"] = previous
    pagevalues["next_image"] = next_image
    if not previous:
        pagevalues["next_next_image"] = next_next_image
    pagevalues["url"] = __SITE_URL + image.image_page_path

    with open(image.image_page_path, "w", encoding="utf-8") as file:
        file.write(gallery_page_template.render(pagevalues))


def create_gallery( # pylint: disable=too-many-locals
    gallery: Gallery, path: str, depth: int = 0, debug_mode: bool = False
) -> None:
    """create_gallery creates the gallery pages
    :param gallery: the Gallery object to create
    :param path: the path to create the gallery in
    :param depth: the depth of the gallery in the directory structure
    :param debug_mode: whether to run in debug mode
    :return: None
    :rtype: None
    :raises: None"""
    logger.info("creating gallery: %s at %s", gallery.name, path)

    for sub_gallery in gallery.sub_galleries:
        subdirectory_name = "".join(c for c in sub_gallery.name if c.isalnum())
        gallery_path = os.path.join(path, subdirectory_name)
        if not os.path.exists(gallery_path):
            os.mkdir(gallery_path)
        sub_gallery.relative_path = subdirectory_name + "/"
        create_gallery(sub_gallery, gallery_path, depth + 1, debug_mode)

    root_path = "/"
    if debug_mode:
        root_path = "../" * depth

    for image in gallery.images:
        image.generate_output_images(path)
        image.image_page = image.name + ".html"

    for image in gallery.images:
        create_image_page(gallery, image, path, root_path, debug_mode)

    # get the page template
    env = jinja2.Environment(loader=jinja2.FileSystemLoader("templates"))
    gallery_page_template = env.get_template("photo-gallery-template.html")

    # get the page variables (which becomes our template dictionary)
    with open("data/pagevariables.json", encoding="utf-8") as file:
        pagevariables = json.load(file)

    # build breadcrumbs
    breadcrumbs = None
    if gallery.parent:
        temp_gallery = gallery.parent
        breadcrumbs = []
        relative_path = "../index.html"
        while temp_gallery:
            breadcrumbs.append((temp_gallery.name, relative_path))
            temp_gallery = temp_gallery.parent
            relative_path = "../" + relative_path
        breadcrumbs.reverse()

    # sorted_galleries = sorted(gallery.sub_galleries, key = lambda g: g.name)
    sorted_galleries = sorted(
        gallery.sub_galleries, key=lambda g: len(g.sub_galleries) * 2 + len(g.images)
    )
    sorted_galleries.reverse()
    sorted_images = sorted(gallery.images, key=lambda i: i.name)

    pagevalues = copy.deepcopy(pagevariables)
    pagevalues["debug_mode"] = debug_mode
    pagevalues["title"] = f"{gallery.name}: a photographic gallery by Kevin Goldsmith"
    pagevalues["galleryname"] = gallery.name
    pagevalues["gallerydescription"] = gallery.description
    pagevalues["rootpath"] = root_path
    pagevalues["subgalleries"] = sorted_galleries
    pagevalues["images"] = sorted_images
    if breadcrumbs:
        pagevalues["breadcrumbs"] = breadcrumbs

    # common.check_for_missing_values(pagevariables, pagevalues)
    with open(os.path.join(path, "index.html"), "w", encoding="utf-8") as file:
        file.write(gallery_page_template.render(pagevalues))


def generate_photo_pages(debug_mode: bool = False) -> None:
    """generate the photo pages for the website"""
    logger.debug("generate_photo_pages")
    top_gallery = Gallery("Albums", __PHOTOS_DIRECTORY)
    top_gallery.populate()
    logger.debug("gallery populated: %s", top_gallery)
    output_directory = os.path.join(common.get_output_directory(debug_mode), "photos/")
    if not os.path.exists(output_directory):
        os.mkdir(output_directory)

    create_gallery(top_gallery, output_directory, 1, debug_mode)


if __name__ == "__main__":
    # parse command line
    parser = argparse.ArgumentParser(description="generate the photos pages")
    parser.add_argument("--debug", action="store_true")
    args = parser.parse_args()
    logger = logging.getLogger(__name__)
    if args.debug:
        # common.initialize_logging(logging.DEBUG)
        common.initialize_logging(logging.INFO)
    else:
        common.initialize_logging(logging.INFO)

    generate_photo_pages(args.debug)
else:
    logger = logging.getLogger()
