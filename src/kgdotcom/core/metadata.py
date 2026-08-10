#!/usr/bin/env python3
# *_* coding: utf-8 *_*

"""structured page metadata: titles, descriptions, canonical URLs, Open Graph,
Twitter cards and schema.org JSON-LD.

Split out of common.py, which had grown past 1000 lines. This code is
self-contained: it reads data/common_meta.json and builds a PageMetadata for a
given page type, with one builder per type registered in generate_page_metadata.
"""

import json

from dataclasses import dataclass
from typing import Dict, List, Optional


@dataclass
class PageMetadata:  # pylint: disable=too-many-instance-attributes
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
    page_type: str, data: Optional[Dict] = None, debug_mode: bool = False
) -> PageMetadata:
    """Generate structured metadata from existing data"""
    # Load base metadata
    with open("data/common_meta.json", "r", encoding="utf-8") as file:
        base_data = json.load(file)
    base_url = (
        "https://kevingoldsmith.com" if not debug_mode else "http://localhost:8000"
    )
    author = base_data.get("author", "Kevin Goldsmith")

    # Default metadata
    metadata = PageMetadata(
        title=f"{author}",
        description="Technology leader, speaker, and creative professional",
        keywords=["technology", "leadership", "software engineering"],
        canonical_url=f"{base_url}/",
        og_title=None,
        og_description=None,
        schema_type="Person",
    )

    # Generate page-specific metadata. A lookup rather than an if/elif chain so
    # adding a page type is one entry, not another branch.
    builders = {
        "writing": _generate_writing_metadata,
        "resume": _generate_resume_metadata,
        "talks": _generate_talks_metadata,
        "talk": _generate_talk_metadata,
        "music": _generate_music_metadata,
        "photos": _generate_photos_metadata,
        "photography": _generate_photos_metadata,
        "photo": _generate_photo_metadata,
        "index": _generate_index_metadata,
    }
    builder = builders.get(page_type)
    if builder is None:
        return metadata
    return builder(metadata, data, base_url, author)


def _extract_keywords_from_text(
    text: str, existing_keywords: Optional[List[str]] = None
) -> List[str]:
    """Extract keywords from text content"""
    if existing_keywords is None:
        existing_keywords = []

    # Simple keyword extraction - split on common delimiters and filter
    stop_words = {
        "the",
        "and",
        "or",
        "but",
        "in",
        "on",
        "at",
        "to",
        "for",
        "of",
        "with",
        "by",
        "a",
        "an",
        "is",
        "are",
        "was",
        "were",
        "be",
        "been",
        "have",
        "has",
        "do",
        "does",
        "did",
        "will",
        "would",
        "could",
        "should",
        "may",
        "might",
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


def _generate_writing_metadata(
    metadata: PageMetadata, data: Optional[Dict], base_url: str, author: str
) -> PageMetadata:
    """Generate metadata for writing page"""
    articles = data.get("articles", []) if data else []

    # Extract data from articles
    latest_article = articles[0] if articles else None

    # Collect all tags as keywords
    keywords = ["writing", "articles", "blog", "technology"]
    for article in articles[:5]:  # Top 5 articles for keywords
        keywords.extend(article.get("tags", []))

    # Add keywords from latest article description
    if latest_article:
        keywords = _extract_keywords_from_text(
            latest_article.get("description", ""), keywords
        )

    # Build description
    if latest_article:
        description = (
            f"Articles and publications by {author}. Latest: {latest_article['name']}"
        )
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


def _generate_resume_metadata(
    metadata: PageMetadata, data: Optional[Dict], base_url: str, author: str
) -> PageMetadata:
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
        keywords = _extract_keywords_from_text(
            summary[:200], keywords
        )  # First part of summary

    description = _truncate_description(
        headline or f"{label} with expertise in technology and engineering"
    )

    metadata.title = f"Resume - {author}"
    metadata.description = description
    metadata.keywords = list(set(keywords))[:10]
    metadata.canonical_url = f"{base_url}/resume.html"
    metadata.og_title = f"{author} - {label}"
    metadata.og_description = description
    metadata.schema_type = "Person"

    return metadata


def _generate_talks_metadata(
    metadata: PageMetadata, data: Optional[Dict], base_url: str, author: str
) -> PageMetadata:
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
        keywords = _extract_keywords_from_text(
            talk_desc[:100], keywords
        )  # First part of description

        talk_topics.append(talk_title)

    # Build description with talk count and topics
    talk_count = len(talks)
    if talk_count > 0:
        description = (
            f"Conference talks and presentations by {author}. "
            f"{talk_count} talks available"
        )
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


def _generate_music_metadata(
    metadata: PageMetadata, data: Optional[Dict], base_url: str, author: str
) -> PageMetadata:
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
        latest_title = latest_release.get("title", "Recent work")
        description = f"Music by {author}. Latest release: {latest_title}"
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


def _generate_photos_metadata(
    metadata: PageMetadata, data: Optional[Dict], base_url: str, author: str
) -> PageMetadata:
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
                description = (
                    f"Photography by {author}. {photo_count} photos "
                    f"across {gallery_count} galleries"
                )
            elif gallery_name and gallery_name != "Albums":
                # Individual gallery page
                description = (
                    f"Photography from {gallery_name} by {author}. {photo_count} photos"
                )
            else:
                # Main photos index or unknown context
                description = f"Photography by {author}. {photo_count} photos"
        else:
            description = f"Photography and visual work by {author}"
    else:
        description = f"Photography and visual work by {author}"

    description = _truncate_description(description)

    # each gallery is its own page: without a per-gallery canonical and title,
    # every gallery would declare itself a duplicate of photography.html
    gallery_url = data.get("gallery_url") if data else None
    gallery_name = data.get("gallery_name", "") if data else ""
    is_named_gallery = bool(gallery_name) and gallery_name != "Albums"

    metadata.title = (
        f"{gallery_name} - Photography - {author}"
        if is_named_gallery
        else f"Photography - {author}"
    )
    metadata.description = description
    metadata.keywords = keywords + ([gallery_name.lower()] if is_named_gallery else [])
    metadata.canonical_url = gallery_url or f"{base_url}/photography.html"
    metadata.og_title = (
        f"{gallery_name} - Photography by {author}"
        if is_named_gallery
        else f"Photography by {author}"
    )
    metadata.og_description = description
    metadata.schema_type = "ImageGallery"

    return metadata


def _generate_photo_metadata(
    metadata: PageMetadata, data: Optional[Dict], base_url: str, author: str
) -> PageMetadata:
    """Generate metadata for individual photo page"""
    keywords = ["photography", "photo", "image", "visual", "gallery"]

    # Extract photo information from data
    data = data or {}
    photo_title = data.get("photo_title", "Untitled Photo")
    photo_description = data.get("photo_description", "")
    gallery_name = data.get("gallery_name", "")
    capture_date = data.get("capture_date", "")
    photo_url = data.get("photo_url", "")

    # Create title and description
    title = f"{photo_title}: a photo by {author}"

    if photo_description:
        description = f"{photo_description} - Photo by {author}"
    elif gallery_name:
        description = f"Photo from {gallery_name} by {author}"
    else:
        description = f"Photo by {author}"

    if capture_date:
        description += f" (captured {capture_date})"

    # Add gallery to keywords if available
    if gallery_name:
        keywords.append(gallery_name.lower())

    description = _truncate_description(description)

    metadata.title = title
    metadata.description = description
    metadata.keywords = keywords
    metadata.canonical_url = photo_url if photo_url else f"{base_url}/photos/"
    metadata.og_title = photo_title
    metadata.og_description = description
    metadata.schema_type = "Photograph"

    return metadata


def _generate_index_metadata(
    metadata: PageMetadata, data: Optional[Dict], base_url: str, author: str
) -> PageMetadata:
    """Generate metadata for index/home page"""
    keywords = [
        "technology",
        "leadership",
        "speaker",
        "musician",
        "photographer",
        "engineer",
    ]

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
            role_text = (
                ", ".join(highlights[:-1]) + f" and {highlights[-1]}"
                if len(highlights) > 1
                else highlights[0]
            )
            description = f"{author} is a technology leader, {role_text}"
        else:
            description = (
                f"{author} - Technology leader, speaker, and creative professional"
            )
    else:
        description = (
            f"{author} - Technology leader, speaker, and creative professional"
        )

    description = _truncate_description(description)

    metadata.title = author
    metadata.description = description
    metadata.keywords = keywords
    metadata.canonical_url = base_url + "/"
    metadata.og_title = author
    metadata.og_description = description
    metadata.schema_type = "Person"

    return metadata


def _generate_talk_metadata(
    metadata: PageMetadata, data: Optional[Dict], base_url: str, author: str
) -> PageMetadata:
    """Generate metadata for an individual talk page"""
    data = data or {}
    talk_title = data.get("talk_title", "Talk")
    talk_description = data.get("talk_description", "")
    talk_url = data.get("talk_url", "")
    presentation_count = data.get("presentation_count", 0)
    conferences = data.get("conferences", [])

    if talk_description:
        description = talk_description
    elif presentation_count > 0:
        times = "time" if presentation_count == 1 else "times"
        description = (
            f"'{talk_title}', a talk by {author}, presented "
            f"{presentation_count} {times}"
        )
        if conferences:
            description += f" including at {conferences[0]}"
    else:
        description = f"'{talk_title}', a talk by {author}"

    keywords = ["talk", "presentation", "conference", "speaking", "keynote"]
    keywords += _extract_keywords_from_text(f"{talk_title} {talk_description}")

    metadata.title = f"{talk_title}: a talk by {author}"
    metadata.description = _truncate_description(description)
    metadata.keywords = list(dict.fromkeys(keywords))[:10]
    metadata.canonical_url = talk_url or f"{base_url}/talks/"
    metadata.og_title = talk_title
    metadata.og_description = metadata.description
    # the page documents a presentation (abstract, slides, recordings), rather
    # than a single scheduled occurrence, so it is not an Event
    metadata.schema_type = "PresentationDigitalDocument"

    return metadata
