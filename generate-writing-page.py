#!/usr/bin/env python

import json
import os
from string import Template
from datetime import date

format_article_template = Template('<li class=\"article\" data-tags=\"$datatags\"><div class=\"articlename\"><a href="$url">$name</a></div><div class=\"articledate\">$formatteddate</div><div class=\"articledescription\">$description</div><ul class="keywordlist">$keywords</ul></li>')
format_article_keyword_template = Template('<li class=\"keyword\">$tag</li>')
format_filter_button_template = Template('<button onclick=\"filterTag(\'articlelist\',\'$tag\')\">$name</button>')
output_directory = 'output/'

def tagifyTag(tag):
	tag = tag.replace(' ', '-')
	return tag.lower()


with open('data/writing.json') as f:
	writings = json.load(f)

#get the page template
with open('templates/writing-template.html') as f:
	writingpagetemplate = Template(f.read())

article_list = ""
tag_set = set()
for writing in writings:
	if len(writing['name']) > 0:
		writing['formatteddate'] = date(*map(int, writing['date'].split("-"))).strftime("%B %d, %Y")
		tag_list = ""
		data_tag_list = []
		for tag in writing['tags']:
			tag_set.add(tag)
			tag_list += format_article_keyword_template.substitute({'tag': tag})
			data_tag_list.append(tagifyTag(tag))
		writing['keywords'] = tag_list
		writing['datatags'] = ' '.join(data_tag_list)
		article_list += format_article_template.substitute(writing)

button_list = ""
for tag in tag_set:
	button_list += format_filter_button_template.substitute({'name': tag, 'tag': tagifyTag(tag)})

if not os.path.exists(output_directory):
	os.makedirs(output_directory)

d = dict(writinglist = article_list, tagbuttons = button_list)
print("writing writing.html")
with open(output_directory+'writing.html', 'w') as f:
	f.write(writingpagetemplate.substitute(d))
