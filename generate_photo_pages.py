#!/usr/bin/env python
# *_* coding: utf-8 *_*

"""
create the talks/ subdirectory of the website
"""

__version__ = "3.0.0"
__author__ = "Kevin Goldsmith"
__copyright__ = "Copyright 2022, Kevin Goldsmith"
__license__ = "MIT"
__status__ = "Production"  # Prototype, Development or Production

import fnmatch
import json
import logging
import os


__PHOTOS_DIRECTORY = "photos"

class Gallery:
    def __init__(self, name, directory) -> None:
        self.name = name
        self.directory = directory
        self.sub_galleries = []
        self.images = []

    def __str__(self) -> str:
        return f"{self.name} / subgalleries: {self.sub_galleries} / images: {len(self.images)}"
    
    def __repr__(self) -> str:
        return str(self)

    def populate(self) -> None:
        items = os.listdir(self.directory)
        for item in items:
            path = os.path.join(self.directory, item)
            if is_image_file(path):
                self.images.append(item)
            elif os.path.isdir(path):
                newgal = Gallery(item, path)
                newgal.populate()
                if (len(newgal.images) > 0) or (len(newgal.sub_galleries) > 0):
                    self.sub_galleries.append(newgal)
        pass


def is_image_file(filename, extensions=['.jpg', '.jpeg', '.gif', '.png']):
    return any(filename.endswith(e) for e in extensions)


def generate_photo_pages(debug_mode: bool = False) -> None:
    top_gallery = Gallery("portfolio", __PHOTOS_DIRECTORY)
    top_gallery.populate()
    print(top_gallery)
    return True

generate_photo_pages()

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