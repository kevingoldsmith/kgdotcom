#!/usr/bin/env python
import copy
from datetime import date
from operator import itemgetter
from urllib.parse import urlparse
import json
import string
import unicodedata
import requests
from bs4 import BeautifulSoup
import common
import argparse
import os
from navigation import generate_nav_talk, get_href_talks, get_talk_root_for_talk, get_talk_url

#format strings - here to simplify editing and iteration
format_youtube_video_embed = '<iframe width="600" height="338" src="https://www.youtube.com/embed/{0}?rel=0" frameborder="0" allowfullscreen></iframe>'
format_photo_div = '<div id=\"photo\">\n<img src=\"{0}\" class=\"aligncenter\"/>\n</div>'
format_presentation_list_item = '<li><span class=\"conferencename\">{0}</span> - <span class=\"conferencedate\">{1}</span> - <span class=\"conferencelocation\">{2}</span></li>'
format_keynote_list_item = '<li><span class=\"conferencename\">{0}</span> (Keynote) - <span class=\"conferencedate\">{1}</span> - <span class=\"conferencelocation\">{2}</span></li>'
format_upcoming_list_item = '<li><span class=\"conferencename\"><a class=\"outbound\" href=\"{0}\">{1}</a></span> - <span class=\"conferencedate\">{2}</span> - <span class=\"conferencelocation\">{3}</span></li>'
format_reactions_list_item = '<li><span class=\"quote\">{0}</span> - <a class=\"outbound\" href=\"{1}\">{2}</a></li>'
format_video_div = '<div id=\"video\">\n<div class=\"subheader\">Recordings</div>\n'
format_other_recordings_list = '<div id=\"othervideos\">\n<div class=\"othersubheader\">Other recordings</div>\n<ul class=\"inlinelist\">{0}\n</ul>\n</div>'
format_other_recordings_list_item = '<li class=\"inlinelistitem\"><a class=\"outbound\" href=\"{0}\">{1} ({2})</a></li>\n'
format_slides_div = '<div id=\"slides\">\n<div class=\"subheader\">Slides</div>\n'
format_other_slides_list = '<div id=\"otherslides\">\n<div class=\"othersubheader\">Other Versions</div>\n<ul class=\"inlinelist\">{0}\n</ul>\n</div>'
format_other_slides_list_item = '<li class=\"inlinelistitem\"><a class=\"outbound\" href=\"{0}\">{1} ({2})</a></li>\n'
format_reactions_div = '<div id=\"reactions\">\n<div class=\"subheader\">Reactions</div>\n<ul>{0}</ul></div>'
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
format_talk_page_title = '{0}: Talks: Kevin Goldsmith'

#string constants
talk_type_keynote = 'keynote'
talk_type_talk = 'talk'
talk_type_panel = 'panel'
talk_type_panel_chair = 'panel (chair)'
talk_type_lab = 'lab'
talk_type_workshop = 'workshop'


# thanks lazyweb
# https://stackoverflow.com/questions/295135/turn-a-string-into-a-valid-filename
def generate_filename(filename):
	filename = filename.replace(' ', '-')
	filename = filename.replace('@', 'at')
	#cleanedFilename = unicodedata.normalize('NFKD', unicode(filename)).encode('ASCII', 'ignore')
	cleanedFilename = filename
	valid_filename_chars = "-_%s%s" % (string.ascii_letters, string.digits)
	newFilename = ''.join(c for c in cleanedFilename if c in valid_filename_chars)
	newFilename = newFilename.replace('--', '-')
	return newFilename.lower()


def get_embed_code_from_videoURL(video_url):
	#https://youtu.be/_67NPdn6ygY
	#https://www.youtube.com/watch?v=7U3cO3h8Pao
	#https://vimeo.com/102774091
	#<iframe width="560" height="315" src="https://www.youtube.com/embed/_67NPdn6ygY?rel=0" frameborder="0" allowfullscreen></iframe>
	#https://developer.vimeo.com/apis/oembed
	parsed = urlparse(video_url)
	youtube_id = ''
	if parsed.netloc == 'youtu.be':
		split = os.path.split(parsed.path)
		youtube_id = split[1]
	elif parsed.netloc == 'www.youtube.com':
		qs = urlparse.parse_qs(parsed.query)
		if 'v' in qs:
			youtube_id = qs['v'][0]
	elif parsed.netloc == 'vimeo.com':
		response = requests.get('https://vimeo.com/api/oembed.json', params={'url': video_url, 'width': 600})
		if response.status_code == 200:
			return response.json()['html']
	if len(youtube_id) > 0:
		return format_youtube_video_embed.format(youtube_id)


def get_embed_code_from_slides_URL(slides_url):
	#https://www.slideshare.net/developers/oembed
	response = requests.get('http://www.slideshare.net/api/oembed/2', params={'url': slides_url, 'format': 'json', 'maxwidth': 600})
	if response.status_code == 200:
		bs = BeautifulSoup(response.json()['html'], 'html.parser')
		aspect_ratio = float(bs.iframe['height']) / float(bs.iframe['width'])
		bs.iframe['width'] = '600'
		bs.iframe['height'] = str(int(600*aspect_ratio))
		return bs.iframe.prettify()


def check_for_missing_values(original, new):
	for key in original.keys():
		if (key in ['description', 'title', 'presentationlist']) and (original[key] == new[key]):
			print("\tWARNING: {0} has default value".format(key))


def is_workshop(talk):
	return 'talk-type' in talk and ((talk['talk-type'] == talk_type_lab) or (talk['talk-type'] == talk_type_workshop))

def is_talk(talk):
	return 'talk-type' in talk and ((talk['talk-type'] == talk_type_talk) or (talk['talk-type'] == talk_type_keynote))

def is_panel(talk):
	return 'talk-type' in talk and ((talk['talk-type'] == talk_type_panel) or (talk['talk-type'] == talk_type_panel_chair))

def get_talk_date(talk):
	return date(*map(int, talk['date'].split("-")))

#parse command line
parser = argparse.ArgumentParser(description='generate the talks pages')
parser.add_argument('--debug', action='store_true')
args = parser.parse_args()
debug_mode = args.debug

#get the conference data
with open('data/conferences.json', 'r') as f:
	conference_talks = json.load(f)

#get the talk page template
with open('templates/talk-page-template.html') as f:
	talkpagetemplate = string.Template(f.read())

#get the page variables (which becomes our template dictionary)
with open('data/pagevariables.json') as f:
	pagevariables = json.load(f)

#create the output director
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
		if get_talk_date(talk) < date.today():
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

	talktitle = talk_index
	filetitle = generate_filename(talktitle)
	outputfilename = filetitle + '.html'
	filepath = output_directory + filetitle + '.html'

	print("creating file: {0}".format(filetitle))

	pagevalues = copy.deepcopy(pagevariables)
	pagevalues['title'] = format_talk_page_title.format(talktitle)
	pagevalues['talktitle'] = talktitle
	pagevalues['filename'] = outputfilename
	recordings = []
	slides = []
	presentations = []
	reactions = []
	conferences = unique_talks[talk_index]
	description = ''

	if os.path.isfile('public/talks/'+filetitle+'.jpg'):
		photofile = filetitle + '.jpg'
		photo = format_photo_div.format(photofile)
		pagevalues['photo'] = photo

	for conference in conferences:
		this_talk = None
		for talk in conference['talks']:
			if (talk_index == talk['talk']) or (('root-talk' in talk) and (talk['root-talk'] == talk_index)):
				this_talk = talk

		if (this_talk is not None):
			#this_talk[u'outputfilename'] = unicode(outputfilename)
			this_talk[u'outputfilename'] = outputfilename
			talk_date = get_talk_date(this_talk)

			if ('talk-description' in this_talk) and (len(this_talk['talk-description']) > len(description)):
				#pick the longest description (figuring it is the most imformative)
				description = this_talk['talk-description']

			conference_name = conference['conference']
			if 'recording-url' in this_talk:
				recordings.append({'date': talk_date, 'recording-url': this_talk['recording-url'], 'conference': conference_name})

			if ('slides-url' in this_talk) and (not any(d.get('slides-url', None) == this_talk['slides-url'] for d in slides)):
				slides.append({'date': talk_date, 'slides-url': this_talk['slides-url'], 'talk': this_talk['talk']})

			conference_location = common.format_city_state_country_from_location(this_talk['location']) if 'location' in this_talk else "virtual"

			talk_list_item_format = format_presentation_list_item
			if this_talk['talk-type'] == talk_type_keynote:
				talk_list_item_format = format_keynote_list_item

			presentations.append(talk_list_item_format.format(conference_name, talk_date.strftime("%B %d, %Y"), conference_location))

			if 'reactions' in this_talk:
				for reaction in this_talk['reactions']:
					quote = reaction['quote']
					credit = reaction['credit']
					ref = reaction['reference-url']
					reactions.append(format_reactions_list_item.format(quote, ref, credit))
			try:
				index = next(index for (index, d) in enumerate(index_page['talks']) if d["name"] == talk_index)
				if talk_date > index_page['talks'][index]['date']:
					index_page['talks'][index]['date'] = talk_date
			except StopIteration:
				index_page['talks'].append({'name': talk_index, 'file': outputfilename, 'date': talk_date})

	if len(description) > 0:
		pagevalues['description'] = description

	if len(recordings) > 0:
		# get the embed code for the first recording, since it is the most recent
		sorted_recordings = sorted(recordings, key=itemgetter('date'), reverse=True)
		embed_url = sorted_recordings[0]['recording-url']
		video_string = format_video_div + get_embed_code_from_videoURL(embed_url)

		other_recordings_string = ''
		if len(sorted_recordings) > 1:
			other_recordings_string = format_other_recordings_list
			iterrecordings = iter(sorted_recordings)
			next(iterrecordings)
			other_recordings_list = ''
			for recording in iterrecordings:
				other_recordings_list += format_other_recordings_list_item.format(recording['recording-url'], recording['conference'], recording['date'].year)
			other_recordings_string = other_recordings_string.format(other_recordings_list)
			video_string += other_recordings_string
		video_string += format_close_div
		pagevalues['video'] = video_string

	if len(slides) > 0:
		sorted_slides = sorted(slides, key=itemgetter('date'), reverse=True)
		embed_url = sorted_slides[0]['slides-url']
		slides_string = format_slides_div + get_embed_code_from_slides_URL(embed_url)

		other_slides_string = ''
		if len(sorted_slides) > 1:
			other_slides_string = format_other_slides_list
			iterslides = iter(sorted_slides)
			next(iterslides)
			other_slides_list = ''
			for slide in iterslides:
				other_slides_list += format_other_slides_list_item.format(slide['slides-url'], slide['talk'], slide['date'].year)
			other_slides_string = other_slides_string.format(other_slides_list)
			slides_string += other_slides_string
		slides_string += format_close_div
		pagevalues['slides'] = slides_string

	if len(presentations) > 0:
		pagevalues['presentationlist'] = '\n'.join(presentations)
	else:
		pagevalues['presentationlist'] = ''

	if len(reactions) > 0:
		reactionstring = format_reactions_div.format('\n'.join(reactions))
		pagevalues['reactions'] = reactionstring
	else:
		pagevalues['reactions'] = ''

	pagevalues['sitenav'] = generate_nav_talk(False, debug_mode)
	pagevalues['siteroot'] = get_href_talks('index.html', debug_mode)
	pagevalues['talkroot'] = get_talk_root_for_talk(debug_mode)

	check_for_missing_values(pagevariables, pagevalues)

	with open(filepath, 'w') as f:
		f.write(talkpagetemplate.substitute(pagevalues))

for conference in panels:
	conference_name = conference['conference']
	for talk in conference['talks']:
		if is_panel(talk):
			talk_date = get_talk_date(talk)
			talk_name = talk['talk']
			index_page['panels'].append({'date': talk_date, 'name': talk_name, 'conference': conference_name})

for conference in labs:
	conference_name = conference['conference']
	for talk in conference['talks']:
		if is_workshop(talk):
			talk_date = get_talk_date(talk)
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
		year = get_talk_date(conference['talks'][0]).year
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

			talk_date = get_talk_date(this_talk)
			conference_name = conference['conference']
			conference_location = common.format_city_state_country_from_location(this_talk['location']) if 'location' in this_talk else 'virtual'

			if 'url' in conference:
				future_talks_list_items.append(format_upcoming_list_item.format(conference['url'], conference_name, talk_date.strftime("%B %d, %Y"), conference_location))
			else:
				future_talks_list_items.append(format_presentation_list_item.format(conference_name, talk_date.strftime("%B %d, %Y"), conference_location))

	future_talks_string = format_future_talks.format('\n'.join(future_talks_list_items))

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
pagevalues['siteroot'] = get_href_talks('index.html', debug_mode)
check_for_missing_values(pagevariables, pagevalues)
with open(output_directory+'index.html', 'w') as f:
	f.write(talkpagetemplate.substitute(pagevalues))
