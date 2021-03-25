#!/usr/bin/env python

import json
import os
import argparse
from string import Template
from datetime import date
from navigation import generate_nav_root, get_href_root
from common import get_output_directory, validate_url

format_article_template = Template('<li class=\"article\" data-tags=\"$datatags\"><div class=\"articlename\"><a href="$url">$name</a></div><div class=\"articledate\">$formatteddate</div><div class=\"articledescription\">$description</div><ul class="keywordlist">$keywords</ul></li>')
format_article_keyword_template = Template('<li class=\"keyword\">$tag</li>')
format_filter_button_template = Template('<button id=\'$tag\' onclick=\"filterTag(\'articlelist\',\'$tag\')\">$name</button>')

output_file = 'writing.html'

parser = argparse.ArgumentParser(description='generate the writings file')
parser.add_argument('--debug', action='store_true')
args = parser.parse_args()
debug_mode = args.debug

def tagifyTag(tag):
	tag = tag.replace(' ', '-')
	return tag.lower()


with open('data/writing.json') as f:
	writings = json.load(f)

writings = sorted(writings, key=lambda k: k['date'], reverse=True)

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
		writing['tags'].sort()
		for tag in writing['tags']:
			tag_set.add(tag)
			tag_list += format_article_keyword_template.substitute({'tag': tag})
			data_tag_list.append(tagifyTag(tag))
		writing['keywords'] = tag_list
		writing['datatags'] = ' '.join(data_tag_list)
		validate_url(writing['url'])
		article_list += format_article_template.substitute(writing)

button_list = ""
for tag in sorted(tag_set):
	button_list += format_filter_button_template.substitute({'name': tag, 'tag': tagifyTag(tag)})

output_directory = get_output_directory(debug_mode)

d = dict(writinglist = article_list, tagbuttons = button_list, sitenav = generate_nav_root(output_file, debug_mode), siteroot = get_href_root('index.html', debug_mode))
print('writing: ' + output_file)
with open(output_directory+output_file, 'w') as f:
	f.write(writingpagetemplate.substitute(d))
