#!/usr/bin/env python

import json
import os
from string import Template

format_article_template = Template('<li><div><a href="$url">$name</a></div></li>')
output_directory = 'output/'

with open('data/writing.json') as f:
	writings = json.load(f)

#get the page template
with open('templates/writing-template.html') as f:
	writingpagetemplate = Template(f.read())

article_list = ""
for writing in writings:
	if len(writing['name']) > 0:
		article_list += format_article_template.substitute(writing)

if not os.path.exists(output_directory):
	os.makedirs(output_directory)

d = dict(writinglist = article_list)
with open(output_directory+'writing.html', 'w') as f:
	f.write(writingpagetemplate.substitute(d))
