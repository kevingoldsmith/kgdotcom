#!/usr/bin/env python

import json
import os
from string import Template
from datetime import date

format_article_template = Template('<li class=\"article\"><div class=\"articlename\"><a href="$url">$name</a></div><div class=\"articledate\">$formatteddate</div><div class=\"articledescription\">$description</div><ul class="keywordlist">$keywords</ul></li>')
format_article_keyword = Template('<li class=\"keyword\">$tag</li>')
output_directory = 'output/'

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
		for tag in writing['tags']:
			tag_set.add(tag)
			tag_list += format_article_keyword.substitute({'tag': tag})
		writing['keywords'] = tag_list
		article_list += format_article_template.substitute(writing)

if not os.path.exists(output_directory):
	os.makedirs(output_directory)

d = dict(writinglist = article_list)
print("writing writing.html")
with open(output_directory+'writing.html', 'w') as f:
	f.write(writingpagetemplate.substitute(d))
