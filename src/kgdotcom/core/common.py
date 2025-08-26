#!/usr/bin/env python3
# *_* coding: utf-8 *_*

"""utility functions"""


import json
import logging
import os
import string

from datetime import date
from typing import Union, Dict, List, Set
from xmlrpc.client import Boolean

import requests
import pycountry  # type: ignore


logger = logging.getLogger(__name__)


# Dependency graph for incremental builds
DEPENDENCIES = {
    "music.html": {
        "data": ["data/music.json"],
        "templates": ["templates/music-template.html", "templates/header.html", "templates/footer.html", "templates/favicon.html"],
        "static": []
    },
    "resume.html": {
        "data": ["data/resume.json"],
        "templates": ["templates/resume-template.html", "templates/header.html", "templates/footer.html", "templates/favicon.html"],
        "static": []
    },
    "writing.html": {
        "data": ["data/writing.json"],
        "templates": ["templates/writing-template.html", "templates/header.html", "templates/footer.html", "templates/favicon.html"],
        "static": []
    },
    "photos/": {
        "data": ["data/pagevariables.json"],
        "templates": ["templates/photo-page-template.html", "templates/photo-gallery-template.html", "templates/header.html", "templates/footer.html", "templates/favicon.html"],
        "static": ["photos/"],
        "output_pattern": "photos/*.html"
    },
    "contact/": {
        "data": ["data/contact_me.json", "data/common_meta.json"],
        "templates": ["templates/contactpage.html", "templates/contactfile.vcf"],
        "static": ["assets/"],
        "output_pattern": "contact/*"
    }
}


def get_output_directory(debug: bool = False) -> str:
    """figure out which directory to write the output files to"""
    debug_output_directory = "testoutput/"
    output_directory = "output/"

    if debug:
        directory = debug_output_directory
    else:
        directory = output_directory

    if not os.path.exists(directory):
        os.makedirs(directory)

    return directory


def obfusticate_email(email_address: str) -> str:
    """generate a hard to mailto link that will make it difficult to grab the addr
    by bots"""
    format_email_character = '<td style="padding: 0px;">{0}</td><!-- blah! -->'
    format_charref_character = "&#{0};"
    format_email = (
        '<a href="mailto:{0}?subject=Saw%20your%20resume">'
        '<table style="border-spacing: 0px;"><tr>{1}</tr></table></a>'
    )

    obfusticated_display_email = ""
    obfusticated_email = ""

    for char in email_address:
        new_char = format_charref_character.format(ord(char))
        obfusticated_email += new_char
        obfusticated_display_email += format_email_character.format(new_char)

    return format_email.format(obfusticated_email, obfusticated_display_email)


def format_year_from_string(datestring: str) -> str:
    """given a datestring, format the year"""
    return date(*map(int, datestring.split("-"))).strftime("%Y")


def format_month_year_from_string(datestring: str) -> str:
    """given a datestring, format the month, and year"""
    return date(*map(int, datestring.split("-"))).strftime("%B %Y")


def format_month_day_year_from_string(datestring: str) -> str:
    """given a datestring, format the day, month, and year"""
    return date(*map(int, datestring.split("-"))).strftime("%B %d, %Y")


def generate_paragraphs_for_lines(string_with_lines: str) -> str:
    """switch a multi-line string into html paragraphs"""
    if not "\n" in string_with_lines:
        return string_with_lines

    start = 0
    end = 0
    lines = []
    while end > -1:
        end = string_with_lines.find("\n", start)
        if end > -1:
            lines.append(string_with_lines[start:end])
        elif start != len(string_with_lines):
            lines.append(string_with_lines[start:])
        start = end + 1

    paragraphs = "".join(f"<p>{line}</p>\n" for line in lines)
    return paragraphs


def format_city_state_country_from_location(location: dict) -> str:
    """given a location, turn it into a nicely formatted city,
    state and country string"""
    format_location_city_country = (
        '<span class="conferencecity">{0}</span>, '
        '<span class="conferencecountry">{1}</span>'
    )
    format_location_city_state_country = (
        '<span class="conferencecity">{0}</span>, '
        '<span class="conferenceState">{1}</span>, '
        '<span class="conferencecountry">{2}</span>'
    )

    city = location["city"] if "city" in location else ""
    state = location["state"] if "state" in location else ""
    country = location["country"] if "country" in location else ""
    if len(country) == 2:
        country = pycountry.countries.get(alpha_2=country).name

    # if there is no location, it is vritual
    conference_location = "virtual"
    if len(state) > 0:
        conference_location = format_location_city_state_country.format(
            city, state, country
        )
    elif len(city) > 0:
        conference_location = format_location_city_country.format(city, country)

    return conference_location


def get_talk_date(talk: dict) -> date:
    """Given a talk, get a date object from it"""
    return date(*map(int, talk["date"].split("-")))


def check_for_missing_values(original: dict, new: dict) -> None:
    """look for values missing in the document keys"""
    for key in original.keys():
        if (key in ["description", "title", "presentationlist"]) and (
            original[key] == new[key]
        ):
            logger.warning("%s has default value", key)


# thanks lazyweb
# https://stackoverflow.com/questions/295135/turn-a-string-into-a-valid-filename
def generate_filename(filename: str) -> str:
    """create a good filename for a URL"""
    filename = filename.replace(" ", "-")
    filename = filename.replace("@", "at")
    # cleanedFilename = unicodedata.normalize(
    # 'NFKD', unicode(filename)).encode('ASCII', 'ignore')
    cleaned_filename = filename
    valid_filename_chars = f"-_{string.ascii_letters}{string.digits}"
    new_filename = "".join(c for c in cleaned_filename if c in valid_filename_chars)
    new_filename = new_filename.replace("--", "-")
    return new_filename.lower()


def validate_url(address: str) -> Boolean:
    """
    given a URL make sure that it is still valid

    Args:
        address (str): the URL to check
    """

    # print(f"validating URL: {address}")
    logger.debug("validating URL: %s", address)
    response = True
    with open("ignore_error_urls.json", "r", encoding="utf-8") as url_file:
        ignore_list = json.load(url_file)

    if address in ignore_list:
        return True

    try:
        resp = requests.get(address, timeout=5.0)
        response = resp.status_code not in [400, 404, 403, 408, 409, 501, 502, 503]
    except requests.exceptions.RequestException:
        response = False

    if not response:
        try:
            logger.warning(
                "URL failed to validate: %s, status code: %s", address, resp.status_code
            )
        except NameError:
            logger.warning("URL failed to validate: %s", address)

    return response


def initialize_logging(
    logging_level: int, logging_file: Union[str, None] = None
) -> None:
    """
    initialize_logging set up logging with formatting for stdout and file

    Args:
        logging_level (int): the logging level
        logging_file (Union[str, None], optional): the file to use. Defaults to None.
    """
    # pylint: disable=W0621
    logger = logging.getLogger()
    logger.setLevel(logging_level)
    formatter = logging.Formatter("%(levelname)s: %(message)s")
    formatter.datefmt = "%Y-%m-%d %H:%M:%S %z"
    console_handler = logging.StreamHandler()
    console_handler.setLevel(logging_level)
    console_handler.setFormatter(formatter)
    logger.addHandler(console_handler)

    if logging_file:
        file_handler = logging.FileHandler(logging_file)
        file_handler.setLevel(logging_level)
        file_formatter = logging.Formatter(
            "%(name)s - %(asctime)s (%(levelname)s): %(message)s"
        )
        file_formatter.datefmt = "%Y-%m-%d %H:%M:%S %z"
        file_handler.setFormatter(file_formatter)
        logger.addHandler(file_handler)


def get_all_dependencies(page_key: str) -> Set[str]:
    """Get all file dependencies for a page, expanding directories"""
    deps = set()
    config = DEPENDENCIES.get(page_key, {})
    
    # Add data and template files
    for dep_type in ["data", "templates", "static"]:
        for dep_path in config.get(dep_type, []):
            if os.path.isdir(dep_path):
                # Expand directory to all files (recursively)
                for root, dirs, files in os.walk(dep_path):
                    for file in files:
                        # Skip hidden files and common non-source files
                        if not file.startswith('.') and not file.endswith(('.pyc', '.DS_Store')):
                            deps.add(os.path.join(root, file))
            else:
                deps.add(dep_path)
    
    return deps


def get_latest_modification_time(dependencies: Set[str]) -> float:
    """Get the latest modification time from all dependencies"""
    latest = 0
    for dep in dependencies:
        if os.path.exists(dep):
            mtime = os.path.getmtime(dep)
            latest = max(latest, mtime)
    return latest


def get_photo_output_files(debug_mode: bool = False) -> List[str]:
    """Get all photo HTML files that should exist based on photo directory structure"""
    photo_outputs = []
    output_dir = get_output_directory(debug_mode)
    photo_output_dir = os.path.join(output_dir, "photos")
    
    def collect_gallery_outputs(directory: str, output_path: str) -> None:
        """Recursively collect output files for a gallery directory"""
        if not os.path.exists(directory):
            return
            
        # Each directory gets an index.html
        index_file = os.path.join(output_path, "index.html")
        photo_outputs.append(index_file)
        
        items = os.listdir(directory)
        for item in items:
            item_path = os.path.join(directory, item)
            
            # Check if it's an image file (matching photo generator logic)
            if os.path.isfile(item_path) and any(item.lower().endswith(ext) for ext in ['.jpg', '.jpeg', '.gif', '.png']):
                # Each image gets its own HTML page
                image_name = os.path.splitext(item)[0]
                image_html = os.path.join(output_path, f"{image_name}.html")
                photo_outputs.append(image_html)
                
                # Each image also generates resized versions (but we don't track those for rebuild logic)
                
            elif os.path.isdir(item_path):
                # Process subdirectory (gallery generator creates alphanumeric directory names)
                subdirectory_name = "".join(c for c in item if c.isalnum())
                sub_output_path = os.path.join(output_path, subdirectory_name)
                collect_gallery_outputs(item_path, sub_output_path)
    
    # Start from the photos directory
    collect_gallery_outputs("photos", photo_output_dir)
    
    return photo_outputs


def get_contact_output_files(debug_mode: bool = False) -> List[str]:
    """Get all contact files that should exist based on contact data"""
    contact_outputs = []
    output_dir = get_output_directory(debug_mode)
    contact_dir = os.path.join(output_dir, "contact")
    
    try:
        with open("data/contact_me.json", "r", encoding="utf-8") as file:
            contact_data = json.load(file)
        
        for contact in contact_data.get("contacts", []):
            # Each contact generates multiple files
            if "filename" in contact:
                html_file = os.path.join(contact_dir, contact["filename"])
                contact_outputs.append(html_file)
            if "vcf_filename" in contact:
                vcf_file = os.path.join(contact_dir, contact["vcf_filename"])
                contact_outputs.append(vcf_file)
                # Also wallpaper file
                filename, _ = os.path.splitext(contact["filename"])
                wallpaper_file = os.path.join(contact_dir, filename + "_wallpaper.png")
                contact_outputs.append(wallpaper_file)
    except (FileNotFoundError, json.JSONDecodeError):
        pass
    
    return contact_outputs


def needs_rebuild(page_key: str, debug_mode: bool = False) -> bool:
    """Determine if a page needs to be rebuilt"""
    output_dir = get_output_directory(debug_mode)
    
    # Handle special cases
    if page_key == "photos/":
        return needs_photos_rebuild(debug_mode)
    elif page_key == "contact/":
        return needs_contacts_rebuild(debug_mode)
    
    # Standard single-file output
    output_file = os.path.join(output_dir, page_key)
    
    if not os.path.exists(output_file):
        return True
    
    dependencies = get_all_dependencies(page_key)
    output_mtime = os.path.getmtime(output_file)
    latest_dep_mtime = get_latest_modification_time(dependencies)
    
    return latest_dep_mtime > output_mtime


def needs_photos_rebuild(debug_mode: bool = False) -> bool:
    """Special handling for photos - check if any photo outputs need rebuilding"""
    dependencies = get_all_dependencies("photos/")
    latest_dep_mtime = get_latest_modification_time(dependencies)
    
    photo_outputs = get_photo_output_files(debug_mode)
    
    # If any photo output is missing or older than dependencies
    for output_file in photo_outputs:
        if not os.path.exists(output_file):
            return True
        if os.path.getmtime(output_file) < latest_dep_mtime:
            return True
    
    return False


def needs_contacts_rebuild(debug_mode: bool = False) -> bool:
    """Special handling for contacts - check if any contact outputs need rebuilding"""
    dependencies = get_all_dependencies("contact/")
    latest_dep_mtime = get_latest_modification_time(dependencies)
    
    contact_outputs = get_contact_output_files(debug_mode)
    
    # If any contact output is missing or older than dependencies
    for output_file in contact_outputs:
        if not os.path.exists(output_file):
            return True
        if os.path.getmtime(output_file) < latest_dep_mtime:
            return True
    
    return False
