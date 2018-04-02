#!/usr/bin/env python

import argparse
from string import Template
from navigation import generate_nav_root, get_href_root
from common import get_output_directory

parser = argparse.ArgumentParser(description='generate the writings file')
parser.add_argument('--debug', action='store_true')
args = parser.parse_args()
debug_mode = args.debug

other_pages = [('index.html', 'templates/site-index-template.html'), ('music.html', 'templates/music-template.html'), ('photography.html', 'templates/photography-template.html')]

for page in other_pages:
	with open(page[1]) as f:
		pagetemplate = Template(f.read())

	d = dict(sitenav=generate_nav_root(page[0], debug_mode), siteroot=get_href_root('index.html', debug_mode))
	print('writing: ' + page[0])
	with open(get_output_directory(debug_mode)+page[0], 'w') as f:
		f.write(pagetemplate.substitute(d))
