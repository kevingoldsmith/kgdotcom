#!/usr/bin/env python

import argparse
from string import Template
from navigation import get_href_root
from common import get_output_directory
import os
import datetime

format_url = '<url><loc>{url}</loc><lastmod>{date}</lastmod></url>'

ignore_files = ['403page.html', '404page.html', 'nortonsw_8ae7e2e0-1022-0.html']

parser = argparse.ArgumentParser(description='generate the sitemap')
parser.add_argument('--debug', action='store_true')
args = parser.parse_args()
debug_mode = args.debug

sitemap_files = []
path = get_output_directory(debug_mode)
for (path, dirs, files) in os.walk(path):
	for file in files:
		ext = os.path.splitext(file)[1]
		if (not file in ignore_files) and (ext == '.html'):
			path_list = path.split(os.sep)
			#cheat since I know that there is only a single depth
			sitemap_files.append((os.path.join(path, file), get_href_root(os.path.join(path_list[1], file), debug_mode)))

sitemap_entries = []
for file in sitemap_files:
	sitemap_entries.append(format_url.format(url=file[1], date=datetime.datetime.fromtimestamp(os.path.getmtime(file[0])).strftime('%Y-%m-%d')))

with open('templates/sitemap-template.xml') as f:
	template = Template(f.read())

d = dict(urllist='\n'.join(sitemap_entries))
print('writing: sitemap.xml')
with open(get_output_directory(debug_mode)+'sitemap.xml', 'w') as f:
	f.write(template.substitute(d))
