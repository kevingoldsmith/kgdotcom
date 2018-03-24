#!/usr/bin/env python

import os

debug_output_directory = 'testoutput/'
output_directory = 'output/'

def get_output_directory(debug=False):
	if debug:
		directory = debug_output_directory
	else:
		directory = output_directory

	if not os.path.exists(directory):
		os.makedirs(directory)

	return directory

	parser = argparse.ArgumentParser(description='Generate a file for the site')