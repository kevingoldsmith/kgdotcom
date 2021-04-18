#!/usr/bin/env python3
# *_* coding: utf-8 *_*

"""utility functions"""

__version__ = "1.0.0"
__author__ = "Kevin Goldsmith"
__copyright__ = "Copyright 2021, Kevin Goldsmith"
__license__ = "MIT"
__status__ = "Production"                               # Prototype, Development or Production

# --------------------------------------------------------------------------------

import os
from datetime import date
import string
import json
import requests
import pycountry

def get_output_directory(debug=False):
    """figure out which directory to write the output files to"""
    debug_output_directory = 'testoutput/'
    output_directory = 'output/'

    if debug:
        directory = debug_output_directory
    else:
        directory = output_directory

    if not os.path.exists(directory):
        os.makedirs(directory)

    return directory


def obfusticate_email(email_address):
    """generate a hard to mailto link that will make it difficult to grab the addr by bots"""
    format_email_character = '<td style="padding: 0px;">{0}</td><!-- blah! -->'
    format_charref_character = '&#{0};'
    format_email = ('<a href="mailto:{0}?subject=Saw%20your%20resume">'
                    '<table style="border-spacing: 0px;"><tr>{1}</tr></table></a>')

    obfusticated_display_email = ''
    obfusticated_email = ''

    for char in email_address:
        new_char = format_charref_character.format(ord(char))
        obfusticated_email += new_char
        obfusticated_display_email += format_email_character.format(new_char)

    return format_email.format(obfusticated_email, obfusticated_display_email)


def format_year_from_string(datestring):
    """given a datestring, format the year"""
    return date(*map(int, datestring.split("-"))).strftime("%Y")


def format_month_year_from_string(datestring):
    """given a datestring, format the month, and year"""
    return date(*map(int, datestring.split("-"))).strftime("%B %Y")


def format_month_day_year_from_string(datestring):
    """given a datestring, format the day, month, and year"""
    return date(*map(int, datestring.split("-"))).strftime("%B %d, %Y")


def generate_paragraphs_for_lines(string_with_lines):
    """switch a multi-line string into html paragraphs"""
    if not '\n' in string_with_lines:
        return string_with_lines

    start=0
    end=0
    lines=[]
    while end>-1:
        end=string_with_lines.find('\n', start)
        if end>-1:
            lines.append(string_with_lines[start:end])
        elif start != len(string_with_lines):
            lines.append(string_with_lines[start:])
        start=end+1

    paragraphs = ''
    for line in lines:
        paragraphs += '<p>{0}</p>\n'.format(line)
    return paragraphs


def format_city_state_country_from_location(location):
    """given a location, turn it into a nicely formatted city, state and country string"""
    format_location_city_country = ('<span class=\"conferencecity\">{0}</span>, '
                                    '<span class=\"conferencecountry\">{1}</span>')
    format_location_city_state_country = ('<span class=\"conferencecity\">{0}</span>, '
        '<span class=\"conferenceState\">{1}</span>, <span class=\"conferencecountry\">{2}</span>')

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


def get_talk_date(talk):
    """Given a talk, get a date object from it"""
    return date(*map(int, talk['date'].split("-")))


def check_for_missing_values(original, new):
    """look for values missing in the document keys"""
    for key in original.keys():
        if (key in ['description', 'title', 'presentationlist']) and (original[key] == new[key]):
            print("\tWARNING: {0} has default value".format(key))


# thanks lazyweb
# https://stackoverflow.com/questions/295135/turn-a-string-into-a-valid-filename
def generate_filename(filename):
    """create a good filename for a URL"""
    filename = filename.replace(' ', '-')
    filename = filename.replace('@', 'at')
    #cleanedFilename = unicodedata.normalize('NFKD', unicode(filename)).encode('ASCII', 'ignore')
    cleaned_filename = filename
    valid_filename_chars = "-_%s%s" % (string.ascii_letters, string.digits)
    new_filename = ''.join(c for c in cleaned_filename if c in valid_filename_chars)
    new_filename = new_filename.replace('--', '-')
    return new_filename.lower()


def validate_url(address):
    """given a URL make sure that it is still valid"""
    response = True
    with open('ignore_error_urls.json', 'r') as url_file:
        ignore_list = json.load(url_file)

    if address in ignore_list:
        return True

    try:
        resp = requests.get(address)
        response = resp.status_code not in [400,404,403,408,409,501,502,503]
    except requests.exceptions.RequestException:
        response = False

    if not response:
        try:
            print(f"URL failed to validate: {address}, status code: {resp.status_code}")
        except NameError:
            print(f"URL failed to validate: {address}")

    return response
