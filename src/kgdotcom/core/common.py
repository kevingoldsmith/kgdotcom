#!/usr/bin/env python3
# *_* coding: utf-8 *_*

"""utility functions"""


import json
import logging
import os
import string

from dataclasses import dataclass
from datetime import date
from typing import Union, Dict, List, Set, Optional
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
    },
    "talks/": {
        "data": ["data/conferences.json", "data/current_talks.json", "data/pagevariables.json"],
        "templates": ["templates/talk-index-template.html", "templates/talk-page-template.html"],
        "static": ["public/talks/"],
        "output_pattern": "talks/*.html"
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


def get_talks_output_files(debug_mode: bool = False) -> List[str]:
    """Get all talk files that should exist based on talk data"""
    talk_outputs = []
    output_dir = get_output_directory(debug_mode)
    talks_dir = os.path.join(output_dir, "talks")
    
    # Always include the main index page
    index_file = os.path.join(talks_dir, "index.html")
    talk_outputs.append(index_file)
    
    # Include static files copied from public/talks/
    public_talks_dir = "public/talks/"
    if os.path.exists(public_talks_dir):
        for item in os.listdir(public_talks_dir):
            if not item.startswith('.'):  # Skip hidden files
                static_output = os.path.join(talks_dir, item)
                talk_outputs.append(static_output)
    
    # Include generated individual talk pages
    try:
        with open("data/conferences.json", "r", encoding="utf-8") as file:
            conference_talks = json.load(file)
        
        unique_talks = set()
        for conference in conference_talks:
            for talk in conference["talks"]:
                # Mirror the logic from talks.py for determining unique talks
                from datetime import date
                if get_talk_date(talk) < date.today():
                    talk_index = talk.get("root-talk", talk["talk"])
                    # Only add talks that get individual pages (talk and keynote types)
                    talk_type = talk.get("talk-type", "")
                    if talk_type in ["talk", "keynote"]:  # Only these types get individual pages
                        if talk_index:
                            unique_talks.add(talk_index)
        
        # Generate output file paths for each unique talk
        for talk_title in unique_talks:
            filename = generate_filename(talk_title) + ".html"
            talk_file = os.path.join(talks_dir, filename)
            talk_outputs.append(talk_file)
            
    except (FileNotFoundError, json.JSONDecodeError):
        pass
    
    return talk_outputs


def needs_rebuild(page_key: str, debug_mode: bool = False) -> bool:
    """Determine if a page needs to be rebuilt"""
    output_dir = get_output_directory(debug_mode)
    
    # Handle special cases
    if page_key == "photos/":
        return needs_photos_rebuild(debug_mode)
    elif page_key == "contact/":
        return needs_contacts_rebuild(debug_mode)
    elif page_key == "talks/":
        return needs_talks_rebuild(debug_mode)
    
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


def needs_talks_rebuild(debug_mode: bool = False) -> bool:
    """Special handling for talks - check if any talk outputs need rebuilding"""
    dependencies = get_all_dependencies("talks/")
    latest_dep_mtime = get_latest_modification_time(dependencies)
    
    talk_outputs = get_talks_output_files(debug_mode)
    
    # If any talk output is missing or older than dependencies
    for output_file in talk_outputs:
        if not os.path.exists(output_file):
            return True
        if os.path.getmtime(output_file) < latest_dep_mtime:
            return True

    return False


@dataclass
class PageMetadata:
    """Structured metadata for web pages"""
    title: str
    description: str
    keywords: List[str]
    canonical_url: str
    og_title: Optional[str] = None
    og_description: Optional[str] = None
    og_image: Optional[str] = None
    og_type: str = "website"
    twitter_card: str = "summary"
    schema_type: Optional[str] = None
    last_modified: Optional[str] = None


def generate_page_metadata(
    page_type: str,
    data: Dict = None,
    debug_mode: bool = False
) -> PageMetadata:
    """Generate structured metadata from existing data"""
    # Load base metadata
    with open("data/common_meta.json", "r", encoding="utf-8") as file:
        base_data = json.load(file)
    base_url = "https://kevingoldsmith.com" if not debug_mode else "http://localhost:8000"
    author = base_data.get("author", "Kevin Goldsmith")

    # Default metadata
    metadata = PageMetadata(
        title=f"{author}",
        description="Technology leader, speaker, and creative professional",
        keywords=["technology", "leadership", "software engineering"],
        canonical_url=f"{base_url}/",
        og_title=None,
        og_description=None,
        schema_type="Person"
    )

    # Generate page-specific metadata
    if page_type == "writing":
        return _generate_writing_metadata(metadata, data, base_url, author)
    elif page_type == "resume":
        return _generate_resume_metadata(metadata, data, base_url, author)
    elif page_type == "talks":
        return _generate_talks_metadata(metadata, data, base_url, author)
    elif page_type == "music":
        return _generate_music_metadata(metadata, data, base_url, author)
    elif page_type == "photos" or page_type == "photography":
        return _generate_photos_metadata(metadata, data, base_url, author)
    elif page_type == "index":
        return _generate_index_metadata(metadata, data, base_url, author)

    return metadata


def _extract_keywords_from_text(text: str, existing_keywords: List[str] = None) -> List[str]:
    """Extract keywords from text content"""
    if existing_keywords is None:
        existing_keywords = []

    # Simple keyword extraction - split on common delimiters and filter
    stop_words = {
        "the", "and", "or", "but", "in", "on", "at", "to", "for", "of", "with",
        "by", "a", "an", "is", "are", "was", "were", "be", "been", "have", "has",
        "do", "does", "did", "will", "would", "could", "should", "may", "might"
    }

    words = []
    for word in text.lower().replace(",", " ").replace(".", " ").split():
        word = word.strip("()[]{}\"'")
        if len(word) > 3 and word not in stop_words and word.isalpha():
            words.append(word)

    # Combine with existing keywords and limit to 10
    all_keywords = list(set(existing_keywords + words))
    return all_keywords[:10]


def _truncate_description(text: str, max_length: int = 155) -> str:
    """Truncate description to SEO-friendly length"""
    if len(text) <= max_length:
        return text

    # Try to truncate at word boundary
    truncated = text[:max_length]
    last_space = truncated.rfind(" ")
    if last_space > max_length - 20:  # Don't truncate too aggressively
        truncated = truncated[:last_space]

    return truncated + "..."


def _generate_writing_metadata(metadata: PageMetadata, data: Dict, base_url: str, author: str) -> PageMetadata:
    """Generate metadata for writing page"""
    articles = data.get("articles", []) if data else []

    # Extract data from articles
    article_count = len(articles)
    latest_article = articles[0] if articles else None

    # Collect all tags as keywords
    keywords = ["writing", "articles", "blog", "technology"]
    for article in articles[:5]:  # Top 5 articles for keywords
        keywords.extend(article.get("tags", []))

    # Add keywords from latest article description
    if latest_article:
        keywords = _extract_keywords_from_text(latest_article.get("description", ""), keywords)

    # Build description
    if latest_article:
        description = f"Articles and publications by {author}. Latest: {latest_article['name']}"
    else:
        description = f"Articles and publications by {author}"

    description = _truncate_description(description)

    metadata.title = f"Writing - {author}"
    metadata.description = description
    metadata.keywords = list(set(keywords))[:10]
    metadata.canonical_url = f"{base_url}/writing.html"
    metadata.og_title = f"Writing by {author}"
    metadata.og_description = description
    metadata.schema_type = "Blog"

    if latest_article:
        metadata.last_modified = latest_article.get("date")

    return metadata


def _generate_resume_metadata(metadata: PageMetadata, data: Dict, base_url: str, author: str) -> PageMetadata:
    """Generate metadata for resume page"""
    basics = data.get("basics", {}) if data else {}

    # Extract professional info
    label = basics.get("label", "Technology Leader")
    headline = basics.get("headline", "")

    # Extract keywords from headline and summary
    keywords = ["resume", "cv", "technology", "leadership", "engineering"]
    if headline:
        keywords = _extract_keywords_from_text(headline, keywords)

    summary = basics.get("summary", "")
    if summary:
        keywords = _extract_keywords_from_text(summary[:200], keywords)  # First part of summary

    description = _truncate_description(headline or f"{label} with expertise in technology and engineering")

    metadata.title = f"Resume - {author}"
    metadata.description = description
    metadata.keywords = list(set(keywords))[:10]
    metadata.canonical_url = f"{base_url}/resume.html"
    metadata.og_title = f"{author} - {label}"
    metadata.og_description = description
    metadata.schema_type = "Person"

    return metadata


def _generate_talks_metadata(metadata: PageMetadata, data: Dict, base_url: str, author: str) -> PageMetadata:
    """Generate metadata for talks page"""
    talks = data.get("talks", []) if data else []

    # Extract talk topics for keywords
    keywords = ["talks", "speaking", "conferences", "presentations"]
    talk_topics = []

    for talk in talks[:5]:  # Top 5 talks
        talk_title = talk.get("talk", "")
        talk_desc = talk.get("description", "")

        # Extract keywords from talk content
        keywords = _extract_keywords_from_text(talk_title, keywords)
        keywords = _extract_keywords_from_text(talk_desc[:100], keywords)  # First part of description

        talk_topics.append(talk_title)

    # Build description with talk count and topics
    talk_count = len(talks)
    if talk_count > 0:
        description = f"Conference talks and presentations by {author}. {talk_count} talks available"
        if talk_topics:
            description += f" including '{talk_topics[0]}'"
    else:
        description = f"Conference talks and presentations by {author}"

    description = _truncate_description(description)

    metadata.title = f"Talks - {author}"
    metadata.description = description
    metadata.keywords = list(set(keywords))[:10]
    metadata.canonical_url = f"{base_url}/talks/"
    metadata.og_title = f"Conference Talks by {author}"
    metadata.og_description = description
    metadata.schema_type = "CreativeWork"

    return metadata


def _generate_music_metadata(metadata: PageMetadata, data: Dict, base_url: str, author: str) -> PageMetadata:
    """Generate metadata for music page"""
    solo_projects = data.get("solo_projects", []) if data else []

    keywords = ["music", "musician", "audio", "creative", "albums"]

    # Extract project and release info
    latest_release = None
    total_releases = 0

    for project in solo_projects:
        project_name = project.get("name", "")
        releases = project.get("releases", [])
        total_releases += len(releases)

        if releases and not latest_release:
            latest_release = releases[0]  # Assuming first is latest

        # Add project name as keyword
        if project_name:
            keywords = _extract_keywords_from_text(project_name, keywords)

    # Build description
    if latest_release:
        description = f"Music by {author}. Latest release: {latest_release.get('title', 'Recent work')}"
    elif total_releases > 0:
        description = f"Music by {author}. {total_releases} releases available"
    else:
        description = f"Music and creative audio work by {author}"

    description = _truncate_description(description)

    metadata.title = f"Music - {author}"
    metadata.description = description
    metadata.keywords = list(set(keywords))[:10]
    metadata.canonical_url = f"{base_url}/music.html"
    metadata.og_title = f"Music by {author}"
    metadata.og_description = description
    metadata.schema_type = "MusicRecording"

    if latest_release:
        year = latest_release.get("year")
        if year:
            metadata.last_modified = f"{year}-01-01"

    return metadata


def _generate_photos_metadata(metadata: PageMetadata, data: Dict, base_url: str, author: str) -> PageMetadata:
    """Generate metadata for photos/photography page"""
    keywords = ["photography", "photos", "visual", "creative", "gallery"]

    # If photo data is provided, extract info
    if data:
        photo_count = data.get("photo_count", 0)
        gallery_count = data.get("gallery_count", 0)
        gallery_name = data.get("gallery_name", "")

        if photo_count > 0:
            if gallery_count > 0:
                # Main photos index with multiple galleries
                description = f"Photography by {author}. {photo_count} photos across {gallery_count} galleries"
            elif gallery_name and gallery_name != "Albums":
                # Individual gallery page
                description = f"Photography from {gallery_name} by {author}. {photo_count} photos"
            else:
                # Main photos index or unknown context
                description = f"Photography by {author}. {photo_count} photos"
        else:
            description = f"Photography and visual work by {author}"
    else:
        description = f"Photography and visual work by {author}"

    description = _truncate_description(description)

    metadata.title = f"Photography - {author}"
    metadata.description = description
    metadata.keywords = keywords
    metadata.canonical_url = f"{base_url}/photography.html"
    metadata.og_title = f"Photography by {author}"
    metadata.og_description = description
    metadata.schema_type = "ImageGallery"

    return metadata


def _generate_index_metadata(metadata: PageMetadata, data: Dict, base_url: str, author: str) -> PageMetadata:
    """Generate metadata for index/home page"""
    keywords = ["technology", "leadership", "speaker", "musician", "photographer", "engineer"]

    # If aggregated data is provided, use it to enhance description
    if data:
        highlights = []
        if data.get("latest_article"):
            highlights.append("writer")
        if data.get("recent_talks"):
            highlights.append("speaker")
        if data.get("music_releases"):
            highlights.append("musician")

        if highlights:
            role_text = ", ".join(highlights[:-1]) + f" and {highlights[-1]}" if len(highlights) > 1 else highlights[0]
            description = f"{author} is a technology leader, {role_text}"
        else:
            description = f"{author} - Technology leader, speaker, and creative professional"
    else:
        description = f"{author} - Technology leader, speaker, and creative professional"

    description = _truncate_description(description)

    metadata.title = author
    metadata.description = description
    metadata.keywords = keywords
    metadata.canonical_url = base_url + "/"
    metadata.og_title = author
    metadata.og_description = description
    metadata.schema_type = "Person"

    return metadata
