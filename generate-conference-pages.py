#!/usr/bin/env python
import json
from datetime import date

with open('conferences.json', 'r') as f:
    conference_talks = json.load(f)

#for conference in conference_talks:
#	for talk in conference['talks']:
#		talkdate = date(*map(int, talk['date'].split("-")))
#		print("{0} - {1} - {2}".format( conference['conference'].encode('utf-8'),
#										talk['talk'].encode('utf-8'),
#										talkdate.strftime("%B %d, %Y")))

unique_talks = {}

for conference in conference_talks:
	for talk in conference['talks']:
		talk_index = ""
#		if 'root-talk' in talk:
#			talk_index = talk['root-talk']
#		else:
#			talk_index = talk['talk']
		
		talk_index = talk['root-talk'] if 'root-talk' in talk else talk['talk']
		
		if len(talk_index) > 0:
			if talk_index in unique_talks:
				unique_talks[talk_index].append(conference)
			else:
				unique_talks[talk_index]=[]
				unique_talks[talk_index].append(conference)

for talk_index in unique_talks:
	print talk_index
	recordings = []
	presentations = []
	reactions = []
	conferences = unique_talks[talk_index]
	for conference in conferences:
		this_talk = None
		for talk in conference['talks']:
			if (talk_index == talk['talk']) or (('root-talk' in talk) and (talk['root-talk'] == talk_index)):
				this_talk = talk

		if (this_talk is not None):
			talkdate = date(*map(int, this_talk['date'].split("-")))
			conference_name = conference['conference']
			if 'recording-url' in this_talk:
				recording = this_talk['recording-url']
				recordings.append("<li><a href=\"{0}\">{1} - {2}</a></li>".format(recording, conference_name, talkdate.strftime("%B, %Y")))
			city = this_talk['location']['city'].encode('utf-8') if 'city' in this_talk['location'] else ""
			country = this_talk['location']['country'].encode('utf-8') if 'country' in this_talk['location'] else ""
			presentations.append("<li><span class=\"conferencename\">{0}</span> - <span class=\"conferencedate\">{1}</span> - <span class=\"conferencecity\">{2}</span>, <span=\"conferencecountry\">{3}</span></li>".format(conference_name.encode('utf-8'), talkdate.strftime("%B %d, %Y"), city, country))
			if 'reactions' in this_talk:
				for reaction in this_talk['reactions']:
					quote = reaction['quote'].encode('utf-8')
					credit = reaction['credit'].encode('utf-8')
					ref = reaction['reference-url'].encode('utf-8')
					reactions.append("<li><span class=\"quote\">{0}</span> - <a href=\"{1}\">{2}</a></li>".format(quote, ref, credit))

	print "RECORDINGS:"
	for recording in recordings:
		print recording

	print "PRESENTED AT:"
	for presentation in presentations:
		print presentation
	print

	print "REACTIONS:"
	for reaction in reactions:
		print reaction
	print

	print

