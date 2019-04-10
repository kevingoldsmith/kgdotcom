#!/usr/bin/env python
import copy
from datetime import date
from operator import itemgetter
import json
import string
import unicodedata
import common
import argparse
from navigation import generate_nav_talk, get_href_root, get_talk_root_for_talk, get_talk_url
from generatetalkpage import generate_talk_page

#format strings - here to simplify editing and iteration
format_presentation_list_item = '<li><span class=\"conferencename\">{0}</span> - <span class=\"conferencedate\">{1}</span> - <span class=\"conferencelocation\">{2}</span></li>'
format_upcoming_list_item = '<li><span class=\"conferencename\"><a class=\"outbound\" href=\"{0}\">{1}</a></span> - <span class=\"conferencedate\">{2}</span> - <span class=\"conferencelocation\">{3}</span></li>'
template_panel_list_item = '<li><span class=\"talk-title\">$name</span>, <span class=\"conference\">$conference</span>, <span class=\"date\">$datestring</span></li>'
template_lab_list_item = '<li><span class=\"talk-title\">$name</span>, <span class=\"conference\">$conference</span>, <span class=\"date\">$datestring</span></li>'
template_talk_list_item = '<li><a href="$file"><span class=\"talk-title\">$name</span></a></li>'
format_featured_talk_list_item = '<li><a href="{0}"><span class=\"talk-title\">{1}</span></a><div class="talk-description">{2}</div></li>'
format_other_talks_list_item = '<li class=\"year-item\">\n<div class=\"year\">{0}</div>\n<ul>\n'
format_close_div = '</div>\n'
format_close_ul = '</ul>\n'
format_close_li = '</li>\n'
format_a = '<a href=\"{0}\">{1}</a>'
format_marker = '[\'{0} {1}\', {2}, {3}]'
format_info_window = '[\'<div class=\"info_content\"><h3>{0} {1}</h3><p>{2}</p></div>\']'
format_future_talks = '<section id=\"upcoming-talks\"><h2>Upcoming Talks</h2><ul>{0}</ul></section>'

#string constants
talk_type_keynote = 'keynote'
talk_type_talk = 'talk'
talk_type_panel = 'panel'
talk_type_panel_chair = 'panel (chair)'
talk_type_lab = 'lab'
talk_type_workshop = 'workshop'


def is_workshop(talk):
	return 'talk-type' in talk and ((talk['talk-type'] == talk_type_lab) or (talk['talk-type'] == talk_type_workshop))

def is_talk(talk):
	return 'talk-type' in talk and ((talk['talk-type'] == talk_type_talk) or (talk['talk-type'] == talk_type_keynote))

def is_panel(talk):
	return 'talk-type' in talk and ((talk['talk-type'] == talk_type_panel) or (talk['talk-type'] == talk_type_panel_chair))

#parse command line
parser = argparse.ArgumentParser(description='generate the talks pages')
parser.add_argument('--debug', action='store_true')
args = parser.parse_args()
debug_mode = args.debug

#get the conference data
with open('data/conferences.json', 'r') as f:
	conference_talks = json.load(f)

#create the output directory
output_directory = common.get_output_directory(debug_mode) + 'talks/'

unique_talks = {}
panels = []
labs = []
upcoming_talks = []

#conference JSON is organized by conference for ease of editing
#but for the purposes of creating pages, we want to store by talks
#so we swizzle
for conference in conference_talks:
	for talk in conference['talks']:
		if common.get_talk_date(talk) < date.today():
			talk_index = ""
			talk_index = talk['root-talk'] if 'root-talk' in talk else talk['talk']
			if is_talk(talk):
				if len(talk_index) > 0:
					if talk_index in unique_talks:
						unique_talks[talk_index].append(conference)
					else:
						unique_talks[talk_index] = [conference]
			elif is_panel(talk):
				panels.append(conference)
			elif is_workshop(talk):
				labs.append(conference)
		else:
			upcoming_talks.append(conference)

index_page = {'talks': [], 'labs': [], 'panels': []}

#now walk through our talk list generating pages for each talk
for talk_index in unique_talks:
	# TODO: refactor this
	index_page = generate_talk_page(talk_index, unique_talks[talk_index], output_directory, index_page, debug_mode)

for conference in panels:
	conference_name = conference['conference']
	for talk in conference['talks']:
		if is_panel(talk):
			talk_date = common.get_talk_date(talk)
			talk_name = talk['talk']
			index_page['panels'].append({'date': talk_date, 'name': talk_name, 'conference': conference_name})

for conference in labs:
	conference_name = conference['conference']
	for talk in conference['talks']:
		if is_workshop(talk):
			talk_date = common.get_talk_date(talk)
			talk_name = talk['talk']
			index_page['labs'].append({'date': talk_date, 'name': talk_name, 'conference': conference_name})

# generate the index page
# get the list of current talks, they will go in a separate section
current_talks = {}
with open('data/current_talks.json') as f:
	current_talk_list = json.load(f)
	for talk in current_talk_list:
		current_talks[talk['talk']] = talk['description']

#generate lis for the panels
panel_list_string = ''
if len(index_page['panels']) > 0:
	sorted_panels = sorted(index_page['panels'], key=itemgetter('date'), reverse=True)
	panel_strings = []
	#add city and conference URL?
	listring = string.Template(template_panel_list_item)
	for panel in sorted_panels:
		panel['datestring'] = panel['date'].strftime("%B %d, %Y")
		panel_strings.append(listring.substitute(panel))
	panel_list_string = '\n'.join(panel_strings)

#generate lis for the labs
lab_list_string = ''
if len(index_page['labs']) > 0:
	sorted_labs = sorted(index_page['labs'], key=itemgetter('date'), reverse=True)
	labs_strings = []
	#add city and conference URL?
	listring = string.Template(template_lab_list_item)
	for lab in sorted_labs:
		lab['datestring'] = lab['date'].strftime("%B %d, %Y")
		labs_strings.append(listring.substitute(lab))
	lab_list_string = '\n'.join(labs_strings)

# create the featured and other talk lists
other_talks_string = ''
featured_talks_string = ''
if len(index_page['talks']) > 0:
	featured_talk_strings = []
	other_talk_strings = []
	sorted_talks = sorted(index_page['talks'], key=itemgetter('date'), reverse=True)
	for talk in sorted_talks:
		talk['file'] = get_talk_url(talk['file'], debug_mode)
		if talk['name'] in current_talks.keys():
			featured_talk_strings.append(format_featured_talk_list_item.format(talk['file'], talk['name'], current_talks[talk['name']]))
		else:
			other_talk_strings.append({'year': talk['date'].year, 'li': string.Template(template_talk_list_item).substitute(talk)})
	featured_talks_string = '\n'.join(featured_talk_strings)

	current_year = 0
	first_year = True
	for other_talk_string in other_talk_strings:
		if current_year != other_talk_string['year']:
			current_year = other_talk_string['year']
			if not first_year:
				other_talks_string += format_close_ul + format_close_li
			else:
				first_year = False
			other_talks_string += format_other_talks_list_item.format(other_talk_string['year'])
		other_talks_string += '{0}\n'.format(other_talk_string['li'])
	other_talks_string += format_close_ul + format_close_li

#get the page template
with open('templates/talk-index-template.html') as f:
	talkpagetemplate = string.Template(f.read())

print("creating index.html")
marker_list = []
info_list = []
for conference in conference_talks:
	if ('location' in conference['talks'][0]) and len(conference['conference']) > 0:
		conference_name = conference['conference'].replace("\'","&apos;")
		year = common.get_talk_date(conference['talks'][0]).year
		lat = conference['talks'][0]['location']['gps'][0]
		log = conference['talks'][0]['location']['gps'][1]
		marker = format_marker.format(conference_name, year, lat, log)
		marker_list.append(marker)

		talks = []
		for talk in conference['talks']:
			talk_name = talk['talk'].replace("\'","&apos;")
			if 'outputfilename' in talk:
				talks.append(format_a.format(get_talk_url(talk['outputfilename'], debug_mode),talk_name))
			else:
				talks.append(talk_name)
		info = format_info_window.format(conference_name, year, '<br />'.join(talks))
		info_list.append(info)

future_talks_string = ''
if len(upcoming_talks) > 0:
	future_talks_list_items = []
	for conference in upcoming_talks:
		this_talk = None
		if len(conference['talks']) > 0:
			this_talk = conference['talks'][0]

			talk_date = common.get_talk_date(this_talk)
			conference_name = conference['conference']
			conference_location = common.format_city_state_country_from_location(this_talk['location']) if 'location' in this_talk else 'virtual'
			item = ''

			if 'url' in conference:
				item = format_upcoming_list_item.format(conference['url'], conference_name, talk_date.strftime("%B %d, %Y"), conference_location)
			else:
				item = format_presentation_list_item.format(conference_name, talk_date.strftime("%B %d, %Y"), conference_location)

			if item not in future_talks_list_items:
				future_talks_list_items.append(item)

	future_talks_string = format_future_talks.format('\n'.join(future_talks_list_items))

#get the page variables (which becomes our template dictionary)
with open('data/pagevariables.json') as f:
	pagevariables = json.load(f)

pagevalues = copy.deepcopy(pagevariables)
pagevalues['currenttalklist'] = featured_talks_string
pagevalues['othertalklist'] = other_talks_string
pagevalues['panellist'] = panel_list_string
pagevalues['workshoplist'] = lab_list_string
pagevalues['title'] = 'Talks: Kevin Goldsmith'
pagevalues['presentationlist'] = ''
pagevalues['description'] = 'Kevin Goldsmith Talks'
pagevalues['markerlist'] = ',\n'.join(marker_list)
pagevalues['infolist'] = ',\n'.join(info_list)
pagevalues['futuretalks'] = future_talks_string
pagevalues['sitenav'] = generate_nav_talk(True, debug_mode)
pagevalues['siteroot'] = get_href_root('index.html', debug_mode, True)
common.check_for_missing_values(pagevariables, pagevalues)
with open(output_directory+'index.html', 'w') as f:
	f.write(talkpagetemplate.substitute(pagevalues))
