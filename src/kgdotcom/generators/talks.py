#!/usr/bin/env python
# *_* coding: utf-8 *_*

"""
create the talks/ subdirectory of the website
"""

__version__ = "2.0.0"
__author__ = "Kevin Goldsmith"
__copyright__ = "Copyright 2021, Kevin Goldsmith"
__license__ = "MIT"
__status__ = "Production"  # Prototype, Development or Production

import argparse
import copy
import json
import logging
import os
from datetime import date
from operator import itemgetter
from typing import Any, Dict, List
from xmlrpc.client import boolean

import jinja2  # type: ignore

from kgdotcom.core import common
from kgdotcom.utils import talk_types as conference_talk_types
from kgdotcom.generators.talk_page import generate_talk_page
from kgdotcom.core.navigation import get_talk_url


def generate_conference_pages(debug_mode: boolean = False) -> None:
    # pylint: disable=R0914, R0912, R0915, R1702
    """Generate the index page and the individual talk pages"""
    # get the conference data
    with open("data/conferences.json", "r", encoding="utf-8") as file:
        conference_talks = json.load(file)

    # create the output directory
    output_directory = os.path.join(common.get_output_directory(debug_mode), "talks/")

    unique_talks: Dict[str, Any] = {}
    panels = []
    labs = []
    upcoming_talks = []

    # conference JSON is organized by conference for ease of editing
    # but for the purposes of creating pages, we want to store by talks
    # so we swizzle
    for conference in conference_talks:
        for talk in conference["talks"]:
            if common.get_talk_date(talk) < date.today():
                talk_index = ""
                talk_index = talk["root-talk"] if "root-talk" in talk else talk["talk"]
                if not conference_talk_types.has_valid_talk_type(talk):
                    logger.error(
                        "%s has invalid type %s",
                        talk["talk"],
                        talk.get("talk-type", "NONE"),
                    )
                if conference_talk_types.is_talk(talk):
                    if len(talk_index) > 0:
                        if talk_index in unique_talks:
                            unique_talks[talk_index].append(conference)
                        else:
                            unique_talks[talk_index] = [conference]
                elif conference_talk_types.is_panel(talk):
                    panels.append(conference)
                elif conference_talk_types.is_workshop(talk):
                    labs.append(conference)
            else:
                upcoming_talks.append(conference)

    index_page: Dict[str, List[Any]] = {"talks": [], "labs": [], "panels": []}

    # now walk through our talk list generating pages for each talk
    for talk_index in unique_talks:  # pylint: disable=consider-using-dict-items
        index_page = generate_talk_page(
            talk_index,
            unique_talks[talk_index],
            output_directory,
            index_page,
            debug_mode,
        )

    for conference in panels:
        conference_name = conference["conference"]
        for talk in conference["talks"]:
            if conference_talk_types.is_panel(talk):
                talk_date = common.get_talk_date(talk)
                talk_name = talk["talk"]
                panel_info = {
                    "date": talk_date,
                    "name": talk_name,
                    "conference": conference_name,
                }
                if "recording-url" in talk:
                    common.validate_url(talk["recording-url"])
                    panel_info["url"] = talk["recording-url"]
                index_page["panels"].append(panel_info)

    for conference in labs:
        conference_name = conference["conference"]
        for talk in conference["talks"]:
            if conference_talk_types.is_workshop(talk):
                talk_date = common.get_talk_date(talk)
                talk_name = talk["talk"]
                index_page["labs"].append(
                    {
                        "date": talk_date,
                        "name": talk_name,
                        "conference": conference_name,
                    }
                )

    # generate the index page
    # get the list of current talks, they will go in a separate section
    current_talks = {}
    with open("data/current_talks.json", encoding="utf-8") as file:
        current_talk_list = json.load(file)
        for talk in current_talk_list:
            current_talks[talk["talk"]] = talk["description"]

    # generate list for the panels
    panel_list = []
    if len(index_page["panels"]) > 0:
        sorted_panels = sorted(
            index_page["panels"], key=itemgetter("date"), reverse=True
        )
        for panel in sorted_panels:
            if "url" in panel:
                common.validate_url(panel["url"])
            panel_list.append(
                {
                    "date": panel["date"].strftime("%B %d, %Y"),
                    "url": panel.get("url"),
                    "name": panel["name"],
                    "conference": panel["conference"],
                }
            )

    # generate list for the labs
    lab_list = []
    if len(index_page["labs"]) > 0:
        sorted_labs = sorted(index_page["labs"], key=itemgetter("date"), reverse=True)
        for lab in sorted_labs:
            lab_list.append(
                {
                    "date": lab["date"].strftime("%B %d, %Y"),
                    "name": lab["name"],
                    "conference": lab["conference"],
                }
            )

    # create the featured and other talk lists
    other_talk_list = []
    featured_talks = []
    if len(index_page["talks"]) > 0:
        other_talks = {}
        sorted_talks = sorted(index_page["talks"], key=itemgetter("date"), reverse=True)
        for talk in sorted_talks:
            talk["file"] = get_talk_url(talk["file"], debug_mode)
            if (
                talk["name"]
                in current_talks.keys()  # pylint: disable=consider-iterating-dictionary
            ):
                # this is a current talk, so we put it in the featured list
                featured_talks.append(
                    {
                        "file": talk["file"],
                        "name": talk["name"],
                        "description": current_talks[talk["name"]],
                    }
                )
            else:
                other_talks[talk["name"]] = {
                    "file": talk["file"],
                    "years": talk["years"],
                }

        sorted_other_talks = sorted(other_talks.keys())
        for other_talk_key in sorted_other_talks:
            other_talk = other_talks[other_talk_key]
            first_year = other_talk["years"][0]
            last_year = other_talk["years"][-1]
            years = ""
            if last_year != first_year:
                years = f"{first_year} - {last_year}"
            else:
                years = f"{last_year}"
            other_talk_list.append(
                {"file": other_talk["file"], "name": other_talk_key, "years": years}
            )

    # get the page template
    env = jinja2.Environment(loader=jinja2.FileSystemLoader("templates"))
    talkpagetemplate = env.get_template("talk-index-template.html")

    logger.info("creating index.html")
    marker_list = []
    info_list = []
    for conference in conference_talks:
        if ("location" in conference["talks"][0]) and len(conference["conference"]) > 0:
            year = common.get_talk_date(conference["talks"][0]).year
            conference_name = conference["conference"].replace("'", "&apos;")
            marker_list.append(
                {
                    "name": conference_name,
                    "year": year,
                    "lat": conference["talks"][0]["location"]["gps"][0],
                    "lon": conference["talks"][0]["location"]["gps"][1],
                }
            )

            talks = []
            for talk in conference["talks"]:
                talk_name = talk["talk"].replace("'", "&apos;")
                if "outputfilename" in talk:
                    talks.append(
                        f"<a href=\"{get_talk_url(talk['outputfilename'], debug_mode)}\">{talk_name}</a>"  # pylint: disable=line-too-long
                    )
                else:
                    talks.append(talk_name)
            info_list.append(
                {"conference_name": conference_name, "year": year, "talks": talks}
            )

    future_talks = []
    if len(upcoming_talks) > 0:
        for conference in upcoming_talks:
            this_talk = None
            if len(conference["talks"]) > 0:
                this_talk = conference["talks"][0]
                talk_date = common.get_talk_date(this_talk)

                conference_name = conference["conference"]
                conference_location = (
                    common.format_city_state_country_from_location(
                        this_talk["location"]
                    )
                    if "location" in this_talk
                    else "virtual"
                )

                if "url" in conference:
                    common.validate_url(conference["url"])

                item = {
                    "url": conference.get("url"),
                    "name": conference_name,
                    "date": talk_date.strftime("%B %d, %Y"),
                    "location": conference_location,
                }

                if item not in future_talks:
                    future_talks.append(item)

    # get the page variables (which becomes our template dictionary)
    with open("data/pagevariables.json", encoding="utf-8") as file:
        pagevariables = json.load(file)

    pagevalues = copy.deepcopy(pagevariables)
    pagevalues["currenttalklist"] = featured_talks
    pagevalues["othertalklist"] = other_talk_list
    pagevalues["panellist"] = panel_list
    pagevalues["workshoplist"] = lab_list
    pagevalues["markerlist"] = marker_list
    pagevalues["infolist"] = info_list
    if len(future_talks) > 0:
        pagevalues["futuretalks"] = future_talks
    pagevalues["debug_mode"] = debug_mode
    # common.check_for_missing_values(pagevariables, pagevalues)
    with open(output_directory + "index.html", "w", encoding="utf-8") as file:
        file.write(talkpagetemplate.render(pagevalues))


if __name__ == "__main__":
    # parse command line
    parser = argparse.ArgumentParser(description="generate the talks pages")
    parser.add_argument("--debug", action="store_true")
    args = parser.parse_args()
    logger = logging.getLogger(__name__)
    common.initialize_logging(logging.INFO)

    generate_conference_pages(args.debug)
else:
    logger = logging.getLogger()
