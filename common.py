#!/usr/bin/env python

import os
import pycountry
from datetime import date

def get_output_directory(debug=False):
	debug_output_directory = 'testoutput/'
	output_directory = 'output/'

	if debug:
		directory = debug_output_directory
	else:
		directory = output_directory

	if not os.path.exists(directory):
		os.makedirs(directory)

	return directory

	parser = argparse.ArgumentParser(description='Generate a file for the site')


def obfusticate_email(email_address):
	format_email_character = '<td style="padding: 0px;">{0}</td><!-- blah! -->'
	format_charref_character = '&#{0};'
	format_email = '<a href="mailto:{0}?subject=Saw%20your%20resume"><table style="border-spacing: 0px;"><tr>{1}</tr></table></a>'

	obfusticated_display_email = ''
	obfusticated_email = ''

	for char in email_address:
		new_char = format_charref_character.format(ord(char))
		obfusticated_email += new_char
		obfusticated_display_email += format_email_character.format(new_char)

	return format_email.format(obfusticated_email, obfusticated_display_email)


def format_year_from_string(datestring):
	return date(*map(int, datestring.split("-"))).strftime("%Y")


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


def format_city_state_country_from_location(location):
	format_location_city_country = '<span class=\"conferencecity\">{0}</span>, <span class=\"conferencecountry\">{1}</span>'
	format_location_city_state_country = '<span class=\"conferencecity\">{0}</span>, <span class=\"conferenceState\">{1}</span>, <span class=\"conferencecountry\">{2}</span>'
	
	city = location['city'] if 'city' in location else ""
	state = location['state'] if 'state' in location else ""
	country = location['country'] if 'country' in location else ""
	if len(country) == 2:
		country = pycountry.countries.get(alpha_2=country).name

	#if there is no location, it is vritual
	conference_location = 'virtual'
	if len(state) > 0:
		conference_location = format_location_city_state_country.format(city, state, country)
	elif len(city) > 0:
		conference_location = format_location_city_country.format(city, country)

	return conference_location