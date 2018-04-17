#!/usr/bin/env python

import unittest
import navigation

class TestNavigation(unittest.TestCase):

	def test_get_href_root(self):
		"""test get_href_root in module navigation"""
		self.assertEqual(navigation.get_href_root('index.html', True), 'index.html')
		self.assertEqual(navigation.get_href_root('../index.html', True), '../index.html')
		self.assertEqual(navigation.get_href_root('index.html', False), 'https://kevingoldsmith.com/')
		#this is bogus as a corner case, but it is the expected behavior, we should fail if it changes
		self.assertEqual(navigation.get_href_root('../index.html', False), 'https://kevingoldsmith.com/../')
		
		self.assertEqual(navigation.get_href_root('resume.html', True), 'resume.html')
		self.assertEqual(navigation.get_href_root('resume.html', False), 'https://kevingoldsmith.com/resume.html')

		self.assertEqual(navigation.get_href_root('talks/index.html', True), 'talks/index.html')
		self.assertEqual(navigation.get_href_root('talks/index.html', False), 'https://kevingoldsmith.com/talks/')

		self.assertEqual(navigation.get_href_root('index.html', True, True), '../index.html')
		self.assertEqual(navigation.get_href_root('../index.html', True, True), '../../index.html')
		self.assertEqual(navigation.get_href_root('index.html', False, True), 'https://kevingoldsmith.com/')
		#this is bogus as a corner case, but it is the expected behavior, we should fail if it changes
		self.assertEqual(navigation.get_href_root('../index.html', False, True), 'https://kevingoldsmith.com/../')
		
		self.assertEqual(navigation.get_href_root('resume.html', True, True), '../resume.html')
		self.assertEqual(navigation.get_href_root('resume.html', False, True), 'https://kevingoldsmith.com/resume.html')

		self.assertEqual(navigation.get_href_root('talks/index.html', True, True), '../talks/index.html')
		self.assertEqual(navigation.get_href_root('talks/index.html', False, True), 'https://kevingoldsmith.com/talks/')

if __name__ == '__main__':
    unittest.main()
