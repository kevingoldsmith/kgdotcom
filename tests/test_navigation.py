#!/usr/bin/env python

import unittest
import navigation

class TestNavigation(unittest.TestCase):

	def test_get_href_root(self):
		"""test get_href_root in module navigation"""
		self.assertEqual(navigation.get_href_root('index.html', True), 'index.html')
		self.assertEqual(navigation.get_href_root('../index.html', True), '../index.html')
		self.assertEqual(navigation.get_href_root('index.html', False), 'https://kevingoldsmith.com/')
		self.assertEqual(navigation.get_href_root('index.html'), 'https://kevingoldsmith.com/')
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


	def test_get_talk_root_for_talk(self):
		"""test get_talk_root_for_talk in module navigation"""
		self.assertEqual(navigation.get_talk_root_for_talk(True), 'index.html')
		self.assertEqual(navigation.get_talk_root_for_talk(False), 'https://kevingoldsmith.com/talks/')
		self.assertEqual(navigation.get_talk_root_for_talk(), 'https://kevingoldsmith.com/talks/')


	def test_get_talk_url(self):
		"""test get_talk_url function in module navigation"""
		self.assertEqual(navigation.get_talk_url('blah'), 'https://kevingoldsmith.com/talks/blah')
		self.assertEqual(navigation.get_talk_url('blah', False), 'https://kevingoldsmith.com/talks/blah')
		self.assertEqual(navigation.get_talk_url('blah', True), 'blah')


	def test_generate_nav_root(self):
		"""test function generate_nav_root in module navigation"""
		self.assertEqual(len(navigation.pages), 5)
		self.assertEqual(navigation.generate_nav_root(''), '<li><a href="https://kevingoldsmith.com/resume.html">technology leader</a></li>\n<li><a href="https://kevingoldsmith.com/talks/">speaker</a></li>\n<li><a href="https://kevingoldsmith.com/writing.html">writer</a></li>\n<li><a href="https://kevingoldsmith.com/music.html">musician</a></li>\n<li><a href="https://kevingoldsmith.com/photography.html">photographer</a></li>')
		self.assertEqual(navigation.generate_nav_root('', False), '<li><a href="https://kevingoldsmith.com/resume.html">technology leader</a></li>\n<li><a href="https://kevingoldsmith.com/talks/">speaker</a></li>\n<li><a href="https://kevingoldsmith.com/writing.html">writer</a></li>\n<li><a href="https://kevingoldsmith.com/music.html">musician</a></li>\n<li><a href="https://kevingoldsmith.com/photography.html">photographer</a></li>')
		self.assertEqual(navigation.generate_nav_root('', True), '<li><a href="resume.html">technology leader</a></li>\n<li><a href="talks/index.html">speaker</a></li>\n<li><a href="writing.html">writer</a></li>\n<li><a href="music.html">musician</a></li>\n<li><a href="photography.html">photographer</a></li>')
		self.assertEqual(navigation.generate_nav_root('resume.html'), '<li class="current-page">technology leader</li>\n<li><a href="https://kevingoldsmith.com/talks/">speaker</a></li>\n<li><a href="https://kevingoldsmith.com/writing.html">writer</a></li>\n<li><a href="https://kevingoldsmith.com/music.html">musician</a></li>\n<li><a href="https://kevingoldsmith.com/photography.html">photographer</a></li>')
		self.assertEqual(navigation.generate_nav_root('resume.html', False), '<li class="current-page">technology leader</li>\n<li><a href="https://kevingoldsmith.com/talks/">speaker</a></li>\n<li><a href="https://kevingoldsmith.com/writing.html">writer</a></li>\n<li><a href="https://kevingoldsmith.com/music.html">musician</a></li>\n<li><a href="https://kevingoldsmith.com/photography.html">photographer</a></li>')
		self.assertEqual(navigation.generate_nav_root('resume.html', True), '<li class="current-page">technology leader</li>\n<li><a href="talks/index.html">speaker</a></li>\n<li><a href="writing.html">writer</a></li>\n<li><a href="music.html">musician</a></li>\n<li><a href="photography.html">photographer</a></li>')
		self.assertEqual(navigation.generate_nav_root('talks/index.html'), '<li><a href="https://kevingoldsmith.com/resume.html">technology leader</a></li>\n<li class="current-page">speaker</li>\n<li><a href="https://kevingoldsmith.com/writing.html">writer</a></li>\n<li><a href="https://kevingoldsmith.com/music.html">musician</a></li>\n<li><a href="https://kevingoldsmith.com/photography.html">photographer</a></li>')
		self.assertEqual(navigation.generate_nav_root('talks/index.html', False), '<li><a href="https://kevingoldsmith.com/resume.html">technology leader</a></li>\n<li class="current-page">speaker</li>\n<li><a href="https://kevingoldsmith.com/writing.html">writer</a></li>\n<li><a href="https://kevingoldsmith.com/music.html">musician</a></li>\n<li><a href="https://kevingoldsmith.com/photography.html">photographer</a></li>')
		self.assertEqual(navigation.generate_nav_root('talks/index.html', True), '<li><a href="resume.html">technology leader</a></li>\n<li class="current-page">speaker</li>\n<li><a href="writing.html">writer</a></li>\n<li><a href="music.html">musician</a></li>\n<li><a href="photography.html">photographer</a></li>')
		self.assertEqual(navigation.generate_nav_root('writing.html'),'<li><a href="https://kevingoldsmith.com/resume.html">technology leader</a></li>\n<li><a href="https://kevingoldsmith.com/talks/">speaker</a></li>\n<li class="current-page">writer</li>\n<li><a href="https://kevingoldsmith.com/music.html">musician</a></li>\n<li><a href="https://kevingoldsmith.com/photography.html">photographer</a></li>')
		self.assertEqual(navigation.generate_nav_root('writing.html', False),'<li><a href="https://kevingoldsmith.com/resume.html">technology leader</a></li>\n<li><a href="https://kevingoldsmith.com/talks/">speaker</a></li>\n<li class="current-page">writer</li>\n<li><a href="https://kevingoldsmith.com/music.html">musician</a></li>\n<li><a href="https://kevingoldsmith.com/photography.html">photographer</a></li>')
		self.assertEqual(navigation.generate_nav_root('writing.html', True), '<li><a href="resume.html">technology leader</a></li>\n<li><a href="talks/index.html">speaker</a></li>\n<li class="current-page">writer</li>\n<li><a href="music.html">musician</a></li>\n<li><a href="photography.html">photographer</a></li>')
		self.assertEqual(navigation.generate_nav_root('music.html'),'<li><a href="https://kevingoldsmith.com/resume.html">technology leader</a></li>\n<li><a href="https://kevingoldsmith.com/talks/">speaker</a></li>\n<li><a href="https://kevingoldsmith.com/writing.html">writer</a></li>\n<li class="current-page">musician</li>\n<li><a href="https://kevingoldsmith.com/photography.html">photographer</a></li>')
		self.assertEqual(navigation.generate_nav_root('music.html', False),'<li><a href="https://kevingoldsmith.com/resume.html">technology leader</a></li>\n<li><a href="https://kevingoldsmith.com/talks/">speaker</a></li>\n<li><a href="https://kevingoldsmith.com/writing.html">writer</a></li>\n<li class="current-page">musician</li>\n<li><a href="https://kevingoldsmith.com/photography.html">photographer</a></li>')
		self.assertEqual(navigation.generate_nav_root('music.html', True), '<li><a href="resume.html">technology leader</a></li>\n<li><a href="talks/index.html">speaker</a></li>\n<li><a href="writing.html">writer</a></li>\n<li class="current-page">musician</li>\n<li><a href="photography.html">photographer</a></li>')
		self.assertEqual(navigation.generate_nav_root('photography.html'), '<li><a href="https://kevingoldsmith.com/resume.html">technology leader</a></li>\n<li><a href="https://kevingoldsmith.com/talks/">speaker</a></li>\n<li><a href="https://kevingoldsmith.com/writing.html">writer</a></li>\n<li><a href="https://kevingoldsmith.com/music.html">musician</a></li>\n<li class="current-page">photographer</li>')
		self.assertEqual(navigation.generate_nav_root('photography.html', False), '<li><a href="https://kevingoldsmith.com/resume.html">technology leader</a></li>\n<li><a href="https://kevingoldsmith.com/talks/">speaker</a></li>\n<li><a href="https://kevingoldsmith.com/writing.html">writer</a></li>\n<li><a href="https://kevingoldsmith.com/music.html">musician</a></li>\n<li class="current-page">photographer</li>')
		self.assertEqual(navigation.generate_nav_root('photography.html', True), '<li><a href="resume.html">technology leader</a></li>\n<li><a href="talks/index.html">speaker</a></li>\n<li><a href="writing.html">writer</a></li>\n<li><a href="music.html">musician</a></li>\n<li class="current-page">photographer</li>')


	def test_generate_nav_talk(self):
		"""test function generate_nav_talk in module navigation"""
		self.assertEqual(navigation.generate_nav_talk(), '<li><a href="https://kevingoldsmith.com/resume.html">technology leader</a></li>\n<li class="current-page"><a href="https://kevingoldsmith.com/talks/">speaker</a></li>\n<li><a href="https://kevingoldsmith.com/writing.html">writer</a></li>\n<li><a href="https://kevingoldsmith.com/music.html">musician</a></li>\n<li><a href="https://kevingoldsmith.com/photography.html">photographer</a></li>')
		self.assertEqual(navigation.generate_nav_talk(False, False), '<li><a href="https://kevingoldsmith.com/resume.html">technology leader</a></li>\n<li class="current-page"><a href="https://kevingoldsmith.com/talks/">speaker</a></li>\n<li><a href="https://kevingoldsmith.com/writing.html">writer</a></li>\n<li><a href="https://kevingoldsmith.com/music.html">musician</a></li>\n<li><a href="https://kevingoldsmith.com/photography.html">photographer</a></li>')
		self.assertEqual(navigation.generate_nav_talk(True, False), '<li><a href="https://kevingoldsmith.com/resume.html">technology leader</a></li>\n<li class="current-page">speaker</li>\n<li><a href="https://kevingoldsmith.com/writing.html">writer</a></li>\n<li><a href="https://kevingoldsmith.com/music.html">musician</a></li>\n<li><a href="https://kevingoldsmith.com/photography.html">photographer</a></li>')
		self.assertEqual(navigation.generate_nav_talk(True), '<li><a href="https://kevingoldsmith.com/resume.html">technology leader</a></li>\n<li class="current-page">speaker</li>\n<li><a href="https://kevingoldsmith.com/writing.html">writer</a></li>\n<li><a href="https://kevingoldsmith.com/music.html">musician</a></li>\n<li><a href="https://kevingoldsmith.com/photography.html">photographer</a></li>')
		self.assertEqual(navigation.generate_nav_talk(True, True), '<li><a href="../resume.html">technology leader</a></li>\n<li class="current-page">speaker</li>\n<li><a href="../writing.html">writer</a></li>\n<li><a href="../music.html">musician</a></li>\n<li><a href="../photography.html">photographer</a></li>')
		self.assertEqual(navigation.generate_nav_talk(False, True), '<li><a href="../resume.html">technology leader</a></li>\n<li class="current-page"><a href="../talks/index.html">speaker</a></li>\n<li><a href="../writing.html">writer</a></li>\n<li><a href="../music.html">musician</a></li>\n<li><a href="../photography.html">photographer</a></li>')

if __name__ == '__main__':
    unittest.main()
