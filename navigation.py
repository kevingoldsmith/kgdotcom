#!/usr/bin/env python

cannonical_root = 'https://kevingoldsmith.com/'
debug_root = ''

# https://kevingoldsmith.com/
# https://kevingoldsmith.com/talks/
# https://kevingoldsmith.com/resume.html

def get_href_root(relative_url, debug=False):
	if not debug:
		return cannonical_root+relative_url.replace('index.html', '')
	return relative_url

def get_href_talks(relative_url, debug=False):
	if not debug:
		return cannonical_root+relative_url.replace('index.html', '')
	return '../'+relative_url

def get_talk_root_for_talk(debug=False):
	if debug:
		return 'index.html'
	return cannonical_root+'talks/'

def get_talk_url(filename, debug=False):
	if debug:
		return filename
	return cannonical_root+'talks/'+filename


#<li><a href="resume.html">technology leader</a></li>
#<li><a href="talks/index.html">speaker</a></li>
#<li class="current-page">writer</li>
#<li><a href="music.html">musician</a></li>
#<li><a href="photography.html">photographer</a></li>

pages = [('resume.html', 'technology leader'), ('talks/index.html', 'speaker'), ('writing.html', 'writer'), ('music.html', 'musician'), ('photography.html', 'photographer')]

format_nav_li = '<li><a href="{url}">{title}</a></li>'
format_nav_li_current = '<li class="current-page">{title}</li>'
def generate_nav_root(current_page, debug=False):
	nav_list = []
	for page in pages:
		if page[0] != current_page:
			nav_list.append(format_nav_li.format(url=get_href_root(page[0], debug), title=page[1]))
		else:
			nav_list.append(format_nav_li_current.format(title=page[1]))
	return '\n'.join(nav_list)


format_talk_nav_li_root = '<li class="current-page">{title}</li>'
format_talk_nav_li_sub = '<li class="current-page"><a href="{url}">{title}</a></li>'
def generate_nav_talk(talk_root=False, debug=False):
	nav_list = []
	for page in pages:
		if page[1] == 'speaker':
			if talk_root:
				nav_list.append(format_talk_nav_li_root.format(url=get_href_talks(page[0], debug), title=page[1]))
			else:
				nav_list.append(format_talk_nav_li_sub.format(url=get_href_talks(page[0], debug), title=page[1]))
		else:
			nav_list.append(format_nav_li.format(url=get_href_talks(page[0], debug), title=page[1]))

	return '\n'.join(nav_list)