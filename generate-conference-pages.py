#!/usr/bin/env python
import json
from datetime import date
from string import Template
import copy
import unicodedata
import string

#thanks lazyweb
#https://stackoverflow.com/questions/295135/turn-a-string-into-a-valid-filename
validFilenameChars = "-_%s%s" % (string.ascii_letters, string.digits)
def generateFilename(filename):
	filename = filename.replace(' ','-')
	filename = filename.replace('@','at')
	cleanedFilename = unicodedata.normalize('NFKD', unicode(filename)).encode('ASCII', 'ignore')
	newFilename = ''.join(c for c in cleanedFilename if c in validFilenameChars)
	return newFilename.lower() + '.html'


#get the data
with open('conferences.json', 'r') as f:
	conference_talks = json.load(f)

#get the page template
with open('talkpagetemplate.html') as f:
	talkpagetemplate = Template( f.read() )

#get the page variables (which becomes our template dictionary)
#the json file looks like
#{
#	"author": "<yourname>",
#	"googsiteverification": "<your google site verification>",
#	"googauthor": "<your google plus url>",
#	"googpublisher": "<your google publisher url>"
#}
with open('pagevariables.json') as f:
	pagevariables = json.load(f)

unique_talks = {}

#conference JSON is organized by conference for ease of editing
#but for the purposes of creating pages, we want to store by talks
#so we swizzle
for conference in conference_talks:
	for talk in conference['talks']:
		talk_index = ""
		talk_index = talk['root-talk'] if 'root-talk' in talk else talk['talk']
		if len(talk_index) > 0:
			if talk_index in unique_talks:
				unique_talks[talk_index].append(conference)
			else:
				unique_talks[talk_index]=[conference]

#now walk through our talk list generating pages for each talk
for talk_index in unique_talks:
	talktitle = talk_index
	print "generating page for {0}".format(talktitle.encode('utf-8'))
	filetitle = generateFilename(talktitle)
	print "creating file: {0}".format(filetitle)

	pagevalues = copy.deepcopy(pagevariables)
	pagevalues['title'] = talktitle
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
			city = this_talk['location']['city'] if 'city' in this_talk['location'] else ""
			country = this_talk['location']['country'] if 'country' in this_talk['location'] else ""
			presentations.append("<li><span class=\"conferencename\">{0}</span> - <span class=\"conferencedate\">{1}</span> - <span class=\"conferencecity\">{2}</span>, <span=\"conferencecountry\">{3}</span></li>".format(conference_name.encode('utf-8'), talkdate.strftime("%B %d, %Y"), city.encode('utf-8'), country.encode('utf-8')))
			if 'reactions' in this_talk:
				for reaction in this_talk['reactions']:
					quote = reaction['quote'].encode('utf-8')
					credit = reaction['credit'].encode('utf-8')
					ref = reaction['reference-url'].encode('utf-8')
					reactions.append('<li><span class=\"quote\">{0}</span> - <a href=\"{1}\">{2}</a></li>'.format(quote, ref, credit))

	if len(recordings) >0:
		print "RECORDINGS:"
		for recording in recordings:
			print recording
		print

	if len(presentations) > 0:
		pagevalues['presentationlist'] = unicode('\n'.join(presentations), 'utf-8')
#		print "PRESENTED AT:"
#		for presentation in presentations:
#			print presentation
#		print
	else:
		pagevalues['presentationlist'] = u''

	if len(reactions) > 0:
		reactionstring = '<div id=\"reactions\">\n<div class=\"subheader\">Reactions</div>\n<ul>'
		reactionstring += '\n'.join(reactions)
		reactionstring += '</ul></div>'
		pagevalues['reactions'] = unicode(reactionstring, 'utf-8')
#		print "REACTIONS:"
#		for reaction in reactions:
#			print reaction
#		print
	else:
		pagevalues['reactions'] = u''

	with open(filetitle, 'w') as f:
		f.write(talkpagetemplate.substitute(pagevalues).encode('utf-8'))

	print