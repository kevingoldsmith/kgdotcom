#!/usr/bin/env python
# *_* coding: utf-8 *_*

"""
create the page for a talk
"""

__version__ = "2.0.0"
__author__ = "Kevin Goldsmith"
__copyright__ = "Copyright 2021, Kevin Goldsmith"
__license__ = "MIT"
__status__ = "Production"                               # Prototype, Development or Production

import urllib
import json
import os
import copy
from datetime import timedelta
from operator import itemgetter
import requests
import requests_cache
from bs4 import BeautifulSoup
import jinja2
import common
from navigation import generate_nav_talk, get_href_root, get_talk_root_for_talk

#requests cache
requests_cache.install_cache(expire_after=timedelta(days=1))
requests_cache.remove_expired_responses()


def get_embed_code_from_video_url(video_url):
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
        parsed_query = urllib.parse.parse_qs(parsed.query)
        if 'v' in parsed_query:
            youtube_id = parsed_query['v'][0]
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


def generate_video_embed(recordings):
    """get an embed string for the video"""
    # get the embed code for the first recording, since it is the most recent
    sorted_recordings = sorted(recordings, key=itemgetter('date'), reverse=True)
    other_recordings = []
    embed_video_string = ''
    for recording in sorted_recordings:
        if len(embed_video_string) == 0:
            embed_url = recording['recording-url']
            common.validate_url(embed_url)
            embed_code = get_embed_code_from_video_url(embed_url)
            if len(embed_code) > 0:
                embed_video_string = embed_code
            else:
                other_recordings.append(recording)
        else:
            other_recordings.append(recording)

    return embed_video_string, other_recordings


def get_embed_code_from_slides_url(slides_url):
    """get the embed code from slideshare given a slideshare URL"""
    #https://www.slideshare.net/developers/oembed
    common.validate_url(slides_url)
    response = requests.get('https://www.slideshare.net/api/oembed/2',
        params={'url': slides_url, 'format': 'json', 'maxwidth': 600})
    if response.status_code == 200:
        soup = BeautifulSoup(response.json()['html'], 'html.parser')
        aspect_ratio = float(soup.iframe['height']) / float(soup.iframe['width'])
        soup.iframe['width'] = '600'
        soup.iframe['height'] = str(int(600*aspect_ratio))
        return soup.iframe.prettify()
    print('ERROR: get slideshare embed failed')
    return None


def generate_talk_page(talk_index, conferences, output_directory, index_page, debug_mode):
    """Generate the page for a talk"""
    #get the talk page template
    env = jinja2.Environment(loader=jinja2.FileSystemLoader('templates'))
    talkpagetemplate = env.get_template('talk-page-template-jinja.html')

    #get the page variables (which becomes our template dictionary)
    with open('data/pagevariables.json') as file:
        pagevariables = json.load(file)

    talktitle = talk_index
    filetitle = common.generate_filename(talktitle)
    outputfilename = filetitle + '-jinja.html'
    filepath = output_directory + filetitle + '-jinja.html'

    print(f"creating file: {filetitle}")

    pagevalues = copy.deepcopy(pagevariables)
    pagevalues['title'] = f'{talktitle}: a talk by Kevin Goldsmith'
    pagevalues['talktitle'] = talktitle
    pagevalues['filename'] = outputfilename
    recordings = []
    slides = []
    presentations = []
    reactions = []
    description = ''

    if os.path.isfile(f'public/talks/{filetitle}.jpg'):
        pagevalues['photo'] = filetitle + '.jpg'

    for conference in conferences:
        this_talk = None
        for talk in conference['talks']:
            if (talk_index == talk['talk']) or (('root-talk' in talk) and
                (talk['root-talk'] == talk_index)):
                this_talk = talk

        if this_talk is not None:
            this_talk[u'outputfilename'] = outputfilename
            talk_date = common.get_talk_date(this_talk)

            if ('talk-description' in this_talk) and (len(this_talk['talk-description']) >
                len(description)):
                #pick the longest description (figuring it is the most imformative)
                description = this_talk['talk-description']

            conference_name = conference['conference']
            if 'recording-url' in this_talk:
                common.validate_url(this_talk['recording-url'])
                recordings.append({
                    'date': talk_date,
                    'recording-url': this_talk['recording-url'],
                    'conference': conference_name})

            if ('slides-url' in this_talk) and (not any(d.get('slides-url', None) ==
                this_talk['slides-url'] for d in slides)):
                common.validate_url(this_talk['slides-url'])
                slides.append(
                    {'date': talk_date,
                    'slides-url': this_talk['slides-url'],
                    'talk': this_talk['talk']})

            conference_location = common.format_city_state_country_from_location(
                this_talk['location']) if 'location' in this_talk else "virtual"

            presentations.append(dict(
                type=this_talk['talk-type'],
                conference_name=conference_name,
                date=talk_date.strftime("%B %d, %Y"),
                location=conference_location
            ))

            if 'reactions' in this_talk:
                for reaction in this_talk['reactions']:
                    if 'reference-url' in reaction:
                        common.validate_url(reaction['reference-url'])
                reactions.extend(this_talk['reactions'])

            try:
                index = next(index for (index, d) in enumerate(index_page['talks']) if
                    d["name"] == talk_index)
                if talk_date > index_page['talks'][index]['date']:
                    index_page['talks'][index]['date'] = talk_date
                index_page['talks'][index]['years'].append(talk_date.year)
            except StopIteration:
                index_page['talks'].append({
                    'name': talk_index,
                    'file': outputfilename,
                    'date': talk_date,
                    'years': [talk_date.year]})

    if len(description) > 0:
        pagevalues['description'] = description

    if len(recordings) > 0:
        video_embed, other_videos = generate_video_embed(recordings)
        pagevalues['video_embed'] = video_embed if len(video_embed) > 0 else None
        pagevalues['other_videos'] = other_videos if len(other_videos) > 0 else None

    if len(slides) > 0:
        sorted_slides = sorted(slides, key=itemgetter('date'), reverse=True)
        embed_url = sorted_slides[0]['slides-url']
        common.validate_url(embed_url)
        pagevalues['slide_embed'] = get_embed_code_from_slides_url(embed_url)

        if len(sorted_slides) > 1:
            pagevalues['other_slides'] = sorted_slides[1:]

    if len(presentations) > 0:
        pagevalues['presentationlist'] = presentations

    if len(reactions) > 0:
        pagevalues['reactions'] = reactions

    pagevalues['sitenav'] = generate_nav_talk(False, debug_mode)
    pagevalues['siteroot'] = get_href_root('index.html', debug_mode, True)
    pagevalues['talkroot'] = get_talk_root_for_talk(debug_mode)
    pagevalues['debug_mode'] = debug_mode

    common.check_for_missing_values(pagevariables, pagevalues)

    with open(filepath, 'w') as file:
        file.write(talkpagetemplate.render(pagevalues))

    return index_page
