#!/usr/bin/env python

import urllib
import string
import json
import os
import common
import requests
import requests_cache
import copy
from datetime import timedelta
from operator import itemgetter
from bs4 import BeautifulSoup
import jinja2
from navigation import generate_nav_talk, get_href_root, get_talk_root_for_talk

#format strings - here to simplify editing and iteration
format_photo_div = '<div id=\"photo\">\n<img src=\"{0}\" class=\"aligncenter\"/>\n</div>'
format_presentation_list_item = '<li><span class=\"conferencename\">{0}</span> - <span class=\"conferencedate\">{1}</span> - <span class=\"conferencelocation\">{2}</span></li>'
format_keynote_list_item = '<li><span class=\"conferencename\">{0}</span> (Keynote) - <span class=\"conferencedate\">{1}</span> - <span class=\"conferencelocation\">{2}</span></li>'
format_upcoming_list_item = '<li><span class=\"conferencename\"><a class=\"outbound\" href=\"{0}\">{1}</a></span> - <span class=\"conferencedate\">{2}</span> - <span class=\"conferencelocation\">{3}</span></li>'
format_reactions_list_item = '<li><span class=\"quote\">{0}</span> - <a class=\"outbound\" href=\"{1}\">{2}</a></li>'
format_reactions_list_item_no_link = '<li><span class=\"quote\">{0}</span> - {1}</li>'
format_video_div = '<div id=\"video\">\n<div class=\"subheader\">Recordings</div>\n'
format_other_recordings_list = '<div id=\"othervideos\">\n<div class=\"othersubheader\">Other recordings</div>\n<ul class=\"inlinelist\">{0}\n</ul>\n</div>'
format_other_recordings_list_no_embeddable = '<ul class=\"inlinelist\">{0}\n</ul>'
format_other_recordings_list_item = '<li class=\"inlinelistitem\"><a class=\"outbound\" href=\"{0}\">{1} ({2})</a></li>\n'
format_slides_div = '<div id=\"slides\">\n<div class=\"subheader\">Slides</div>\n'
format_other_slides_list = '<div id=\"otherslides\">\n<div class=\"othersubheader\">Other Versions</div>\n<ul class=\"inlinelist\">{0}\n</ul>\n</div>'
format_other_slides_list_item = '<li class=\"inlinelistitem\"><a class=\"outbound\" href=\"{0}\">{1} ({2})</a></li>\n'
format_reactions_div = '<div id=\"reactions\">\n<div class=\"subheader\">Reactions</div>\n<ul>{0}</ul></div>'
format_talk_page_title = '{0}: Talks: Kevin Goldsmith'


#duplicated. meh.
format_close_div = '</div>\n'
talk_type_keynote = 'keynote'


#requests cache
requests_cache.install_cache(expire_after=timedelta(days=1))
requests_cache.remove_expired_responses()


def get_embed_code_from_videoURL(video_url):
	"""Generate the html to embed a video given the link to the original video"""
	#https://youtu.be/_67NPdn6ygY
	#https://www.youtube.com/watch?v=7U3cO3h8Pao
	#https://vimeo.com/102774091
	#<iframe width="560" height="315" src="https://www.youtube.com/embed/_67NPdn6ygY?rel=0"
	# 	frameborder="0" allowfullscreen></iframe>
	#https://developer.vimeo.com/apis/oembed
	#https://www.turingfest.com/2019/speakers/kevin-goldsmith?wvideo=46th18adn3
	common.validate_url(video_url)
	parsed = urllib.parse.urlparse(video_url)
	youtube_id = ''
	if parsed.netloc == 'youtu.be':
		split = os.path.split(parsed.path)
		youtube_id = split[1]
	elif parsed.netloc == 'www.youtube.com':
		qs = urllib.parse.parse_qs(parsed.query)
		if 'v' in qs:
			youtube_id = qs['v'][0]
	elif parsed.netloc == 'vimeo.com':
		response = requests.get('https://vimeo.com/api/oembed.json',
								params={'url': video_url, 'width': 600})
		if response.status_code == 200:
			return response.json()['html']
	if len(youtube_id) > 0:
		return ('<iframe width="600" height="338" '
				'src="https://www.youtube-nocookie.com/embed/{0}?rel=0" frameborder="0" '
				'allowfullscreen></iframe>').format(youtube_id)
	
	return ''


def get_embed_code_from_slides_URL(slides_url):
	"""get the embed code from slideshare given a slideshare URL"""
	#https://www.slideshare.net/developers/oembed
	common.validate_url(slides_url)
	response = requests.get('https://www.slideshare.net/api/oembed/2',
		params={'url': slides_url, 'format': 'json', 'maxwidth': 600})
	if response.status_code == 200:
		bs = BeautifulSoup(response.json()['html'], 'html.parser')
		aspect_ratio = float(bs.iframe['height']) / float(bs.iframe['width'])
		bs.iframe['width'] = '600'
		bs.iframe['height'] = str(int(600*aspect_ratio))
		return bs.iframe.prettify()


def generate_talk_page(talk_index, conferences, output_directory, index_page, debug_mode):
	#get the talk page template
	env = jinja2.Environment(loader=jinja2.FileSystemLoader('templates'))
	talkpagetemplate = env.get_template('talk-page-template-jinja.html')

	#get the page variables (which becomes our template dictionary)
	with open('data/pagevariables.json') as f:
		pagevariables = json.load(f)

	talktitle = talk_index
	filetitle = common.generate_filename(talktitle)
	outputfilename = filetitle + '-jinja.html'
	filepath = output_directory + filetitle + '-jinja.html'

	print("creating file: {0}".format(filetitle))

	pagevalues = copy.deepcopy(pagevariables)
	pagevalues['title'] = format_talk_page_title.format(talktitle)
	pagevalues['talktitle'] = talktitle
	pagevalues['filename'] = outputfilename
	recordings = []
	slides = []
	presentations = []
	reactions = []
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
			this_talk[u'outputfilename'] = outputfilename
			talk_date = common.get_talk_date(this_talk)

			if ('talk-description' in this_talk) and (len(this_talk['talk-description']) > len(description)):
				#pick the longest description (figuring it is the most imformative)
				description = this_talk['talk-description']

			conference_name = conference['conference']
			if 'recording-url' in this_talk:
				common.validate_url(this_talk['recording-url'])
				recordings.append({'date': talk_date, 'recording-url': this_talk['recording-url'], 'conference': conference_name})

			if ('slides-url' in this_talk) and (not any(d.get('slides-url', None) == this_talk['slides-url'] for d in slides)):
				common.validate_url(this_talk['slides-url'])
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
					if 'reference-url' in reaction:
						common.validate_url(reaction['reference-url'])
						reactions.append(format_reactions_list_item.format(quote, reaction['reference-url'], credit))
					else:
						reactions.append(format_reactions_list_item_no_link.format(quote, credit))
			try:
				index = next(index for (index, d) in enumerate(index_page['talks']) if d["name"] == talk_index)
				if talk_date > index_page['talks'][index]['date']:
					index_page['talks'][index]['date'] = talk_date
				index_page['talks'][index]['years'].append(talk_date.year)
			except StopIteration:
				index_page['talks'].append({'name': talk_index, 'file': outputfilename, 'date': talk_date, 'years': [talk_date.year]})

	if len(description) > 0:
		pagevalues['description'] = description

	if len(recordings) > 0:
		# get the embed code for the first recording, since it is the most recent
		sorted_recordings = sorted(recordings, key=itemgetter('date'), reverse=True)
		other_recordings = []
		video_string = ''
		for recording in sorted_recordings:
			if len(video_string) == 0:
				embed_url = recording['recording-url']
				common.validate_url(embed_url)
				embed_code = get_embed_code_from_videoURL(embed_url)
				if len(embed_code) > 0:
					video_string = format_video_div + embed_code
				else:
					other_recordings.append(recording)
			else:
				other_recordings.append(recording)

		other_recordings_string = ''
		if len(other_recordings) > 0:
			if len(video_string) < 1:
				video_string = format_video_div
				other_recordings_string = format_other_recordings_list_no_embeddable
			else:
				other_recordings_string = format_other_recordings_list
			other_recordings_list = ''
			for recording in other_recordings:
				other_recordings_list += format_other_recordings_list_item.format(recording['recording-url'], recording['conference'], recording['date'].year)
			other_recordings_string = other_recordings_string.format(other_recordings_list)
			video_string += other_recordings_string
		video_string += format_close_div
		pagevalues['video'] = video_string

	if len(slides) > 0:
		sorted_slides = sorted(slides, key=itemgetter('date'), reverse=True)
		embed_url = sorted_slides[0]['slides-url']
		common.validate_url(embed_url)
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
	pagevalues['siteroot'] = get_href_root('index.html', debug_mode, True)
	pagevalues['talkroot'] = get_talk_root_for_talk(debug_mode)

	common.check_for_missing_values(pagevariables, pagevalues)

	with open(filepath, 'w') as f:
		f.write(talkpagetemplate.render(pagevalues))

	return index_page
