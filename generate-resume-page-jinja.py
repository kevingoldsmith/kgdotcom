#!/usr/bin/env python

import argparse
import json
from string import Template
from common import *
import jinja2

parser = argparse.ArgumentParser(description='generate the writings file')
parser.add_argument('--debug', action='store_true')
args = parser.parse_args()
debug_mode = args.debug

output_page = 'resume-jinja.html'


def format_job_list(work):
	job_list = []
	for work_item in work:
		if 'website' in work_item:
			validate_url(work_item['website'])
		d = dict(
			title=work_item['position'],
			from_date=format_month_year_from_string(work_item['startDate']),
			to_date=format_month_year_from_string(work_item['endDate']) if 'endDate' in work_item else 'present',
			company=work_item['company'],
			website=work_item.get('website'),
			city=work_item['location'],
			description=generate_paragraphs_for_lines(work_item['summary']),
			jobstatus='alumniOf' if 'endDate' in work_item else 'worksFor'
			)
		job_list.append(d)

	return job_list


def format_patent_list(patents):
	patent_list = []
	for patent in patents:
		validate_url(patent['url'])
		d = dict(
			title=patent['name'],
			url=patent['url'],
			number=patent['number'],
			author='co-author' if len(patent['authors']) > 0 else 'sole author',
			filing_date=format_month_day_year_from_string(patent['filingDate']),
			granted_date=format_month_day_year_from_string(patent['grantedDate']),
			abstract=patent['abstract']
			)
		patent_list.append(d)

	return patent_list


#no point in treating this like a list, I only have the one degree :)
def format_education(education_item):
	d = education_item.copy()
	d['grad_date'] = format_month_year_from_string(education_item['endDate'])
	return d


def format_interview_list(interviews):
	interview_list = []
	for interview in interviews:
		validate_url(interview['url'])
		interview['date'] = format_month_year_from_string(interview['date'])
		interview_list.append(interview)
	return interview_list


def format_keynote_list(conferences):
	keynote_list = []
	for conference in conferences:
		for talk in conference['talks']:
			if talk['talk-type'] == 'keynote':
				if not 'talk-url' in talk:
					talk_path = os.path.join('talks', generate_filename(talk['root-talk'] if 'root-talk' in talk else talk['talk'])) + '.html'
					if os.path.exists(os.path.join(get_output_directory(debug_mode),talk_path)):
						talk['talk-url'] = talk_path
				else:
					validate_url(talk['talk-url'])
				d = dict(
					talk=talk['talk'],
					talk_url=talk.get('talk-url'),
					conference=conference['conference'],
					conference_url=conference.get('url'),
					date=format_month_year_from_string(talk['date']),
					location=format_city_state_country_from_location(talk['location']) if 'location' in talk else 'virtual'
					)
				keynote_list.append(d)
	return keynote_list


# get the template
env = jinja2.Environment(loader=jinja2.FileSystemLoader('templates'))
pagetemplate = env.get_template('resume-template-jinja.html')

#get the conference data
with open('data/conferences.json', 'r') as f:
	conference_data = json.load(f)

#get the resume data
with open('data/resume.json', 'r') as f:
	resume_data = json.load(f)

#get the interview data
with open('data/interviews.json', 'r') as f:
	interview_data = json.load(f)

publications = list()
for publication in resume_data['publications']:
	if 'releaseDate' in publication:
		publication['year'] = format_year_from_string(publication['releaseDate'])
	publications.append(publication)

page_variables = dict(
	debug_mode=debug_mode,
	email=obfusticate_email(resume_data['basics']['email']),
	website=resume_data['basics']['website'],
	headline=resume_data['basics']['headline'],
	summary=resume_data['basics']['summary'],
	job_list=format_job_list(resume_data['work']),
	patent_list=format_patent_list(resume_data['patents']),
	education=format_education(resume_data['education'][0]),
	interview_list=format_interview_list(interview_data),
	keynote_list=format_keynote_list(list(reversed(conference_data))),
	publication_list=publications,
	production_list=resume_data['productionCredits'],
	honor_list=resume_data['awards']
	)

print('writing: '+output_page)
with open(get_output_directory(debug_mode)+output_page, 'w') as f:
	f.write(pagetemplate.render(page_variables))
