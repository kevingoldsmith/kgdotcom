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
from shutil import copyfile

import jinja2  # type: ignore
from PIL import Image as PILImage
from PIL.ExifTags import TAGS

import common

__PHOTOS_DIRECTORY = "photos"
__GALLERY_PHOTO_MAX = (2000,2000)
__GALLERY_THUMB_MAX = (1000,1000)

class Gallery:
    def __init__(self, name:str, directory:str) -> None:
        self.name = name
        self.description = ""
        self.output_path = ""
        self.directory = directory
        self.sub_galleries = []
        self.images = []

    def __str__(self) -> str:
        return f"{self.name} / subgalleries: {self.sub_galleries} / images: {self.images}"
    
    def __repr__(self) -> str:
        return str(self)

    def populate(self) -> None:
        items = os.listdir(self.directory)
        for item in items:
            path = os.path.join(self.directory, item)
            if Image.is_image_file(path):
                self.images.append(Image(item, path))
            elif os.path.isdir(path):
                newgal = Gallery(item, path)
                newgal.populate()
                if (len(newgal.images) > 0) or (len(newgal.sub_galleries) > 0):
                    self.sub_galleries.append(newgal)
        self.load_JSON_metadata()

    def load_JSON_metadata(self) -> None:
        json_file = os.path.join(self.directory, self.name + ".json")
        if os.path.exists(json_file):
            with open(json_file, 'r') as f:
                image_data = json.load(f)
                self.name = image_data.get('name', self.name)
                self.description = image_data.get('description', '')


class Image:
    def __init__(self, name:str, path:str) -> None:
        self.name = name
        self.path = path
        self.exif = {}
        self.initialize_EXIF()
        self.load_JSON_overrides()

    def __str__(self) -> str:
        return f"{self.name} - {self.path}"

    def __repr__(self) -> str:
        return str(self)
    
    def initialize_EXIF(self) -> None:
        pil_image = PILImage.open(self.path)
        self.exif['format'] = pil_image.format
        self.exif['size'] = pil_image.size
        exif_tags = pil_image.getexif()
        for tag_id in exif_tags:
            # get the tag name, instead of human unreadable tag id
            tag = TAGS.get(tag_id, tag_id)
            data = exif_tags.get(tag_id)
            # decode bytes 
            if isinstance(data, bytes):
                data = data.decode()
            self.exif[tag] = data
    
    def load_JSON_overrides(self) -> None:
        root_name = os.path.splitext(self.path)[0]
        json_file = root_name + ".json"
        if os.path.exists(json_file):
            with open(json_file, 'r') as f:
                image_data = json.load(f)
                self.name = image_data.get('name', self.name)
                self.description = image_data.get('description', '')

    def generate_output_images(self, destination_path:str) -> None:
        self.output_filename = os.path.basename(self.path)
        self.output_file_path = os.path.join(destination_path, self.output_filename)
        copyfile(self.path, self.output_file_path)

    def is_image_file(filename:str, extensions=['.jpg', '.jpeg', '.gif', '.png']):
        return any(filename.endswith(e) for e in extensions)


def create_gallery(gallery:Gallery, path:str, depth:int = 0, debug_mode:bool = False) -> None:
    logging.info("creating gallery: %s at %s", gallery.name, path)
    
    for sub_gallery in gallery.sub_galleries:
        subdirectory_name = "".join(c for c in sub_gallery.name if c.isalnum())
        gallery_path = os.path.join(path, subdirectory_name)
        if not os.path.exists(gallery_path):
            os.mkdir(gallery_path)
        sub_gallery.relative_path = subdirectory_name + "/"
        create_gallery(sub_gallery, gallery_path, depth+1, debug_mode)
    
    for image in gallery.images:
        image.generate_output_images(path)

    root_path = "/"
    if debug_mode:
        root_path = "../" * depth
    
    # get the page template
    env = jinja2.Environment(loader=jinja2.FileSystemLoader("templates"))
    gallery_page_template = env.get_template("photo-gallery-template.html")

    # get the page variables (which becomes our template dictionary)
    with open("data/pagevariables.json") as file:
        pagevariables = json.load(file)

    pagevalues = copy.deepcopy(pagevariables)
    pagevalues["debug_mode"] = debug_mode
    pagevalues["title"] = f"{gallery.name}: a photographic gallery by Kevin Goldsmith"
    pagevalues["galleryname"] = gallery.name
    pagevalues["gallerydescription"] = gallery.description
    pagevalues["rootpath"] = root_path
    pagevalues["subgalleries"] = gallery.sub_galleries
    pagevalues["images"] = gallery.images

    # common.check_for_missing_values(pagevariables, pagevalues)
    with open(os.path.join(path, "index.html"), "w") as file:
        file.write(gallery_page_template.render(pagevalues))


def generate_photo_pages(debug_mode: bool = False) -> None:
    logger.debug("generate_photo_pages")
    top_gallery = Gallery("portfolio", __PHOTOS_DIRECTORY)
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
        #common.initialize_logging(logging.DEBUG)
        common.initialize_logging(logging.INFO)
    else:    
        common.initialize_logging(logging.INFO)

    generate_photo_pages(args.debug)
else:
    logger = logging.getLogger()


""" # FROM OPEN AI
import os

# Create an empty dictionary
nested_dict = {}

# Define a function to recursively traverse the directory tree and build the dictionary
def build_dict(directory, nested_dict):
  # Get the list of items in the current directory
  items = os.listdir(directory)

  # Iterate over the items
  for item in items:
    # Get the full path of the item
    item_path = os.path.join(directory, item)

    # Check if the item is a directory
    if os.path.isdir(item_path):
      # If it is a directory, create an empty dictionary for it
      nested_dict[item] = {}

      # Recursively traverse the directory tree and build the dictionary
      build_dict(item_path, nested_dict[item])
    else:
      # If it is a file, add it to the dictionary
      nested_dict[item] = None

# Start the recursive traversal of the directory tree from the current directory
build_dict(os.getcwd(), nested_dict)

# Print the resulting dictionary
print(nested_dict)


# FROM OPENAI USING WALK
import os

# Create an empty dictionary
nested_dict = {}

# Use os.walk() to iterate over the items in the directory tree
for root, dirs, files in os.walk("."):
  # Create an empty dictionary for the current directory
  nested_dict[root] = {}

  # Iterate over the directories in the current directory
  for dir in dirs:
    # Add the directory to the dictionary
    nested_dict[root][dir] = {}

  # Iterate over the files in the current directory
  for file in files:
    # Add the file to the dictionary
    nested_dict[root][file] = None

# Print the resulting dictionary
print(nested_dict)
 """