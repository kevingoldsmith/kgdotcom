#!/usr/bin/env python

import argparse
import json
from string import Template
from navigation import generate_nav_root, get_href_root
from common import *
import jinja2

parser = argparse.ArgumentParser(description='generate the writings file')
parser.add_argument('--debug', action='store_true')
args = parser.parse_args()
debug_mode = args.debug

output_page = 'resume-jinja.html'


def format_job_list(work):
	format_company_name = u'<span itemprop="name">{0}</span>'
	format_company_url = u'<a class="outbound" href="{0}" target="_blank">{1}</a>'
	format_job_li = u'<li itemprop="{jobstatus}" itemscope itemtype="http://schema.org/Organization"><div class="job-header"><div class="job-title">{title}</div><div class="job-dates">{from_date} - {to_date}</div><div class="job-company">{company}</div><div class="job-city">{city}</div></div><div class="job-description" itemprop="description">{description}</div></li>'

	job_list = []
	for work_item in work:
		company_name = format_company_name.format(work_item['company'])
		if 'website' in work_item:
			validate_url(work_item['website'])
		d = dict(
			title=work_item['position'],
			from_date=format_month_year_from_string(work_item['startDate']),
			to_date=format_month_year_from_string(work_item['endDate']) if 'endDate' in work_item else 'present',
			company=format_company_url.format(work_item['website'], company_name) if 'website' in work_item else company_name,
			city=work_item['location'],
			description=generate_paragraphs_for_lines(work_item['summary']),
			jobstatus='alumniOf' if 'endDate' in work_item else 'worksFor'
			)
		job_list.append(format_job_li.format(**d))

	return u'\n'.join(job_list)


def format_patent_list(patents):
	format_patent_li = '<li><div class="patent-header"><div class="patent-title"><a class="outbound" href="{url}" target="_blank">{title}</a></div><div class="patent-number">#{number}</div><div class="patent-authorship">{author}</div><div class="patent-filing-date">filed: {filing_date}</div><div class="patent-granted-date">granted: {granted_date}</div></div><div class="patent-abstract">{abstract}</div></li>'
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
		patent_list.append(format_patent_li.format(**d))

	return u'\n'.join(patent_list)


#no point in treating this like a list, I only have the one degree :)
def format_education(education_item):
	format_education_text='<span itemprop="alumniOf" itemscope itemtype="http://schema.org/CollegeOrUniversity"><a class="outbound" itemprop="sameAs" href="{website}"><span class="university-name" itemprop="name">{institution}</span></a>, {location}. {studyType} Degree in {area}, graduated {grad_date}. {summary}</span>'
	education_item['grad_date']=format_month_year_from_string(education_item['endDate'])
	return format_education_text.format(**education_item)


def format_interview_list(interviews):
	format_interview_li = u'<li><a class="outbound" href="{url}">{name}</a>, {date}, {credit}</li>'
	format_credit_author_publisher = '{0} - {1}'
	format_credit_either = '{0}'

	interview_list = []
	for interview in interviews:
		validate_url(interview['url'])
		if ('author' in interview) and ('publisher' in interview):
			interview['credit'] = format_credit_author_publisher.format(interview['author'], interview['publisher'])
		else:
			interview['credit'] = format_credit_either.format(interview['author'] if 'author' in interview else interview['publisher'])

		interview['date'] = format_month_year_from_string(interview['date'])
		interview_list.append(format_interview_li.format(**interview))
	return u'\n'.join(interview_list)


def format_keynote_list(conferences):
	format_keynote_li = '<li><span class="talk-title">{talk}</span>, {conference}, {date}, {location}</li>'
	format_conference_with_link='<a class="outbound" href="{conference_url}">{conference_name}</a>'
	format_talk_with_link='<a href="{talk_url}">{talk}</a>'

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
					talk=format_talk_with_link.format(**dict(talk_url=talk['talk-url'], talk=talk['talk'])) if 'talk-url' in talk else talk['talk'],
					conference=format_conference_with_link.format(**dict(conference_url=conference['url'],conference_name=conference['conference'])) if 'url' in conference else conference['conference'],
					date=format_month_year_from_string(talk['date']),
					location=format_city_state_country_from_location(talk['location']) if 'location' in talk else 'virtual'
					)
				keynote_list.append(format_keynote_li.format(**d))
	return '\n'.join(keynote_list)


# get the template
with open('templates/resume-template-jinja.html') as f:
	pagetemplate = jinja2.Template(f.read())

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
	sitenav=generate_nav_root(output_page, debug_mode),
	siteroot=get_href_root('index.html', debug_mode),
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
