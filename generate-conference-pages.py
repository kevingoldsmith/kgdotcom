#!/usr/bin/env python
import copy
from datetime import date
from operator import itemgetter
import json
import string
import unicodedata
import os

#thanks lazyweb
#https://stackoverflow.com/questions/295135/turn-a-string-into-a-valid-filename
validFilenameChars = "-_%s%s" % (string.ascii_letters, string.digits)
def generateFilename(filename):
	filename = filename.replace(' ', '-')
	filename = filename.replace('@','at')
	cleanedFilename = unicodedata.normalize('NFKD', unicode(filename)).encode('ASCII', 'ignore')
	newFilename = ''.join(c for c in cleanedFilename if c in validFilenameChars)
	newFilename = newFilename.replace('--', '-')
	return newFilename.lower() + '.html'


#get the data
with open('conferences.json', 'r') as f:
	conference_talks = json.load(f)

#get the page template
with open('talkpagetemplate.html') as f:
	talkpagetemplate = string.Template( f.read() )

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

#create the output director
output_directory = 'talks/'
if not os.path.exists(output_directory):
	os.makedirs(output_directory)

unique_talks = {}
panels = []
labs = []

#conference JSON is organized by conference for ease of editing
#but for the purposes of creating pages, we want to store by talks
#so we swizzle
for conference in conference_talks:
	for talk in conference['talks']:
		talk_index = ""
		talk_index = talk['root-talk'] if 'root-talk' in talk else talk['talk']
		if 'talk-type' in talk and talk['talk-type'] == 'talk':
			if len(talk_index) > 0:
				if talk_index in unique_talks:
					unique_talks[talk_index].append(conference)
				else:
					unique_talks[talk_index]=[conference]
		elif 'talk-type' in talk and talk['talk-type'] == 'panel':
			panels.append(conference)
		elif 'talk-type' in talk and talk['talk-type'] == 'lab':
			labs.append(conference)

index_page = {'talks': [], 'labs': [], 'panels': []}

#now walk through our talk list generating pages for each talk
for talk_index in unique_talks:
	talktitle = talk_index
	print "generating page for {0}".format(talktitle.encode('utf-8'))
	filetitle = generateFilename(talktitle)
	filepath = output_directory + filetitle
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
			try:
				index = next(index for (index, d) in enumerate(index_page['talks']) if d["name"] == talk_index)
				if talkdate > index_page['talks'][index]['date']:
					index_page['talks'][index]['date'] = talkdate
			except StopIteration:
				index_page['talks'].append({'name':talk_index, 'file': filetitle, 'date': talkdate})

	if len(recordings) > 0:
		print "RECORDINGS:"
		for recording in recordings:
			print recording
		print

	if len(presentations) > 0:
		pagevalues['presentationlist'] = unicode('\n'.join(presentations), 'utf-8')
	else:
		pagevalues['presentationlist'] = u''

	if len(reactions) > 0:
		reactionstring = '<div id=\"reactions\">\n<div class=\"subheader\">Reactions</div>\n<ul>'
		reactionstring += '\n'.join(reactions)
		reactionstring += '</ul></div>'
		pagevalues['reactions'] = unicode(reactionstring, 'utf-8')
	else:
		pagevalues['reactions'] = u''

	with open(filepath, 'w') as f:
		f.write(talkpagetemplate.substitute(pagevalues).encode('utf-8'))

	print


for conference in panels:
	conference_name = conference['conference']
	for talk in conference['talks']:
		if 'talk-type' in talk and talk['talk-type'] == 'panel':
			talk_date = date(*map(int, talk['date'].split("-")))
			talk_name = talk['talk']
			index_page['panels'].append({'date': talk_date, 'name': talk_name, 'conference': conference_name})

for conference in labs:
	conference_name = conference['conference']
	for talk in conference['talks']:
		if 'talk-type' in talk and talk['talk-type'] == 'lab':
			talk_date = date(*map(int, talk['date'].split("-")))
			talk_name = talk['talk']
			index_page['labs'].append({'date': talk_date, 'name': talk_name, 'conference': conference_name})

# generate the index page
# get the list of current talks, they will go in a separate section
with open('current_talks.json') as f:
	current_talks = json.load(f)

#generate lis for the panels
panel_list_string = ''
if len(index_page['panels']) > 0:
	sorted_panels = sorted(index_page['panels'], key=itemgetter('date'), reverse=True)
	panel_strings = []
	#add city and conference URL?
	listring = string.Template('<li><span class=\"talk-title\">$name</span>, <span class=\"conference\">$conference</span>, <span class=\"date\">$datestring</span></li>')
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
	listring = string.Template('<li><span class=\"talk-title\">$name</span>, <span class=\"conference\">$conference</span>, <span class=\"date\">$datestring</span></li>')
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
	listring = string.Template('<li><a href="$file"><span class=\"talk-title\">$name</span></a></li>')
	for talk in sorted_talks:
		if talk['name'] in current_talks:
			featured_talk_strings.append(listring.substitute(talk))
		else:
			other_talk_strings.append({'year':talk['date'].year, 'li':listring.substitute(talk)})
	featured_talks_string = '\n'.join(featured_talk_strings)

	current_year = 0
	first_year = True
	for other_talk_string in other_talk_strings:
		if current_year != other_talk_string['year']:
			current_year = other_talk_string['year']
			if not first_year:
				other_talks_string += "</ul>\n</li>\n"
			else:
				first_year = False
			other_talks_string += '<li>\n<div class=\"year\">{0}</div>\n<ul>\n'.format(other_talk_string['year'])
		other_talks_string += '{0}\n'.format(other_talk_string['li'])
	other_talks_string += '</ul>\n</li>\n'

#get the page template
with open('indexpagetemplate.html') as f:
	talkpagetemplate = string.Template( f.read() )

pagevalues = copy.deepcopy(pagevariables)
pagevalues['currenttalklist'] = featured_talks_string
pagevalues['othertalklist'] = unicode(other_talks_string, 'utf-8')
pagevalues['panellist'] = panel_list_string
pagevalues['workshoplist'] = lab_list_string
with open(output_directory+'index.html', 'w') as f:
	f.write(talkpagetemplate.substitute(pagevalues).encode('utf-8'))
