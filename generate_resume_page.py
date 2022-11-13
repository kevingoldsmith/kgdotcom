#!/usr/bin/env python3
# *_* coding: utf-8 *_*

"""
create the resume.html page for my website
"""

__version__ = "2.0.0"
__author__ = "Kevin Goldsmith"
__copyright__ = "Copyright 2021, Kevin Goldsmith"
__license__ = "MIT"
__status__ = "Production"  # Prototype, Development or Production

import argparse
import json
import logging
import os
from typing import List

import jinja2  # type: ignore
from xmlrpc.client import boolean

import common


logger = logging.getLogger()


def format_job_list(work: List[dict]) -> List[dict]:
    """cleanup the job data from the resume.json for output"""
    job_list = []
    for work_item in work:
        if "website" in work_item:
            common.validate_url(work_item["website"])
        job = dict(
            title=work_item["position"],
            from_date=common.format_month_year_from_string(work_item["startDate"]),
            to_date=common.format_month_year_from_string(work_item["endDate"])
            if "endDate" in work_item
            else "present",
            company=work_item["company"],
            website=work_item.get("website"),
            city=work_item["location"],
            description=common.generate_paragraphs_for_lines(work_item["summary"]),
            jobstatus="alumniOf" if "endDate" in work_item else "worksFor",
        )
        job_list.append(job)

    return job_list


def format_patent_list(patents: List[dict]) -> List[dict]:
    """cleanup the patent data from the resume.json for output"""
    patent_list = []
    for patent in patents:
        common.validate_url(patent["url"])
        patent = dict(
            title=patent["name"],
            url=patent["url"],
            number=patent["number"],
            author="co-author" if len(patent["authors"]) > 0 else "sole author",
            filing_date=common.format_month_day_year_from_string(patent["filingDate"]),
            granted_date=common.format_month_day_year_from_string(
                patent["grantedDate"]
            ),
            abstract=patent["abstract"],
        )
        patent_list.append(patent)

    return patent_list


# no point in treating this like a list, I only have the one degree :)
def format_education(education_item: dict) -> dict:
    """cleanup the education data from the resume.json for output"""
    college = education_item.copy()
    college["grad_date"] = common.format_month_year_from_string(
        education_item["endDate"]
    )
    return college


def format_interview_list(interviews: List[dict]) -> List[dict]:
    """cleanup the interview list data from the resume.json for output"""
    interview_list = []
    for interview in interviews:
        common.validate_url(interview["url"])
        interview["date"] = common.format_month_year_from_string(interview["date"])
        interview_list.append(interview)
    return interview_list


def format_keynote_list(conferences: List[dict], debug_mode: boolean) -> List[dict]:
    """create a list of conference keynotes from the conferences.json"""
    keynote_list = []
    for conference in conferences:
        for talk in conference["talks"]:
            if talk["talk-type"] == "keynote":
                if not "talk-url" in talk:
                    talk_path = (
                        os.path.join(
                            "talks",
                            common.generate_filename(
                                talk["root-talk"]
                                if "root-talk" in talk
                                else talk["talk"]
                            ),
                        )
                        + ".html"
                    )
                    if os.path.exists(
                        os.path.join(common.get_output_directory(debug_mode), talk_path)
                    ):
                        talk["talk-url"] = talk_path
                    else:
                        logger.error(
                            f"ERROR: talk-path does not exist for {talk['talk']}!"
                        )
                else:
                    common.validate_url(talk["talk-url"])
                keynote = dict(
                    talk=talk["talk"],
                    talk_url=talk.get("talk-url"),
                    conference=conference["conference"],
                    conference_url=conference.get("url"),
                    date=common.format_month_year_from_string(talk["date"]),
                    location=common.format_city_state_country_from_location(
                        talk["location"]
                    )
                    if "location" in talk
                    else "virtual",
                )
                keynote_list.append(keynote)
    return keynote_list


def generate_resume_page(
    debug_mode: boolean = True, output_file: str = "resume.html"
) -> None:
    """generate the resume page for the website from the structured data"""
    # get the template
    env = jinja2.Environment(loader=jinja2.FileSystemLoader("templates"))
    pagetemplate = env.get_template("resume-template.html")

    # get the conference data
    with open("data/conferences.json", "r") as file:
        conference_data = json.load(file)

    # get the resume data
    with open("data/resume.json", "r") as file:
        resume_data = json.load(file)

    # get the interview data
    with open("data/interviews.json", "r") as file:
        interview_data = json.load(file)

    publications = list()
    for publication in resume_data["publications"]:
        if "releaseDate" in publication:
            publication["year"] = common.format_year_from_string(
                publication["releaseDate"]
            )
        publications.append(publication)

    page_variables = dict(
        debug_mode=debug_mode,
        email=common.obfusticate_email(resume_data["basics"]["email"]),
        website=resume_data["basics"]["website"],
        headline=resume_data["basics"]["headline"],
        summary=resume_data["basics"]["summary"],
        job_list=format_job_list(resume_data["work"]),
        patent_list=format_patent_list(resume_data["patents"]),
        education=format_education(resume_data["education"][0]),
        interview_list=format_interview_list(interview_data),
        keynote_list=format_keynote_list(list(reversed(conference_data)), debug_mode),
        publication_list=publications,
        production_list=resume_data["productionCredits"],
        honor_list=resume_data["awards"],
    )

    output_path = os.path.join(common.get_output_directory(debug_mode), output_file)
    logger.info(f"writing: {output_path}")
    with open(output_path, "w") as file:
        file.write(pagetemplate.render(page_variables))


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="generate the writings file")
    parser.add_argument("--debug", action="store_true")
    args = parser.parse_args()
    logger = logging.getLogger(__name__)
    common.initialize_logging(logging.INFO)

    generate_resume_page(debug_mode=args.debug, output_file="resume.html")
