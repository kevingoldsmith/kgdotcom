#!/usr/bin/env python

import argparse
import json
from datetime import date
from string import Template
from navigation import generate_nav_root, get_href_root
from common import get_output_directory

parser = argparse.ArgumentParser(description='generate the writings file')
parser.add_argument('--debug', action='store_true')
args = parser.parse_args()
debug_mode = args.debug

output_page = 'resume.html'


def obfusticate_email(email_address):
	format_email_character = '<td>{0}</td><!-- blah! -->'
	format_charref_character = '&#{0};'
	format_email = '<a href="mailto:{0}?subject=Saw%20your%20resume"><table cellpadding="0" cellspacing="0"><tr>{1}</tr></table></a>'

	obfusticated_display_email = ''
	obfusticated_email = ''

	for char in email_address:
		new_char = format_charref_character.format(ord(char))
		obfusticated_email += new_char
		obfusticated_display_email += format_email_character.format(new_char)

	return format_email.format(obfusticated_email, obfusticated_display_email)

def format_month_year_from_string(datestring):
	return date(*map(int, datestring.split("-"))).strftime("%B %Y")

def format_month_day_year_from_string(datestring):
	return date(*map(int, datestring.split("-"))).strftime("%B %d, %Y")

def generate_paragraphs_for_lines(string_with_lines):
	if not '\n' in string_with_lines:
		return string_with_lines
	
	start=0
	end=0
	lines=[]
	while end>-1:
		end=string_with_lines.find('\n', start)
		if end>-1:
			lines.append(string_with_lines[start:end])
		else:
			lines.append(string_with_lines[start:])
		start=end+1

	paragraphs = ''
	for line in lines:
		paragraphs += '<p>{0}</p>\n'.format(line)
	return paragraphs


def format_job_list(work):
	format_company_url = u'<a class="outbound" href="{0}" target="_blank">{1}</a>'
	format_job_li = u'<li><div class="job-header"><div class="job-title">{title}</div><div class="job-dates">{from_date} - {to_date}</div><div class="job-company">{company}</div><div class="job-city">{city}</div></div><div class="job-description">{description}</div></li>'

	job_list = []
	for work_item in work:
		d = dict(
			title=work_item['position'],
			from_date=format_month_year_from_string(work_item['startDate']),
			to_date=format_month_year_from_string(work_item['endDate']) if 'endDate' in work_item else 'present',
			company=format_company_url.format(work_item['website'],work_item['company']) if 'website' in work_item else work_item['company'],
			city=work_item['location'],
			description=generate_paragraphs_for_lines(work_item['summary'])
			)
		job_list.append(format_job_li.format(**d))

	return u'\n'.join(job_list)


def format_patent_list(patents):
	format_patent_li = '<li><div class="patent-header"><div class="patent-title"><a class="outbound" href="{url}" target="_blank">{title}</a></div><div class="patent-number">#{number}</div><div class="patent-authorship">{author}</div><div class="patent-filing-date">filed: {filing_date}</div><div class="patent-granted-date">granted: {granted_date}</div></div><div class="patent-abstract">{abstract}</div></li>'
	patent_list = []
	for patent in patents:
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
	format_education_text='<a class="outbound" href="{website}"><apan class="university-name">{institution}</span></a>, {location}. {studyType} Degree in {area}, graduated {grad_date}. {summary}'
	education_item['grad_date']=format_month_year_from_string(education_item['endDate'])
	return format_education_text.format(**education_item)


def format_interview_list(interviews):
	format_interview_li = u'<li><a class="outbound" href="{url}">{name}</a>, {date}, {credit}</li>'
	format_credit_author_publisher = '{0} - {1}'
	format_credit_either = '{0}'

	interview_list = []
	for interview in interviews:
		if ('author' in interview) and ('publisher' in interview):
			interview['credit'] = format_credit_author_publisher.format(interview['author'], interview['publisher'])
		else:
			interview['credit'] = format_credit_either.format(interview['author'] if 'author' in interview else interview['publisher'])

		interview['date'] = format_month_year_from_string(interview['date'])
		interview_list.append(format_interview_li.format(**interview))
	return u'\n'.join(interview_list)


#<li><span class="talk-title"><a href="http://blog.kevingoldsmith.com/2017/05/13/my-talk-and-interview-from-jax-2017-in-mainz-germany/" class="outbound">Fail Fast, Fail Safe... Succeed! (Opening Keynote)</a></span>, <a class="outbound" href="https://jax.de/">JAX 2017</a>, May 2017, Mainz, Germany</li>
def format_keynote_list(conferences):
	format_keynote_li = '<li><span class="talk-title"><a href="{talk_url}">{talk}</a></span>, <a class="outbound" href="{conference_url}">{conference_name}</a>, {date}, {location}</li>'
	
	keynote_list = []
	for conference in confereces:
		for talk in conference['talks']:
			if talk['talk-type'] = 'keynote':



# get the template
with open('templates/resume-template.html') as f:
	pagetemplate = Template(f.read())

#get the conference data
with open('data/conferences.json', 'r') as f:
	conference_data = json.load(f)

#get the resume data
with open('data/resume.json', 'r') as f:
	resume_data = json.load(f)

#get the interview data
with open('data/interviews.json', 'r') as f:
	interview_data = json.load(f)

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
	interview_list=format_interview_list(interview_data)
	)


print('writing: '+output_page)
with open(get_output_directory(debug_mode)+output_page, 'w') as f:
	f.write(pagetemplate.substitute(page_variables))
