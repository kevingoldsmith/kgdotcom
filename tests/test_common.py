#!/usr/bin/env python

import unittest
import os
import common

class TestCommon(unittest.TestCase):
	def test_get_output_directory(self):
		"""test the get_output_directory function"""

		#delete the directories if they are there?
		self.assertEqual(common.get_output_directory(True), 'testoutput/')
		self.assertTrue(os.path.exists('testoutput/'))

		self.assertEqual(common.get_output_directory(False), 'output/')
		self.assertTrue(os.path.exists('output/'))


	def test_obfusticate_email(self):
		"""test the obfusticate_email function"""
		# valid e-mail address
		self.assertEqual(common.obfusticate_email('dev@null.com'), '<a href="mailto:&#100;&#101;&#118;&#64;&#110;&#117;&#108;&#108;&#46;&#99;&#111;&#109;?subject=Saw%20your%20resume"><table style="border-spacing: 0px;"><tr><td style="padding: 0px;">&#100;</td><!-- blah! --><td style="padding: 0px;">&#101;</td><!-- blah! --><td style="padding: 0px;">&#118;</td><!-- blah! --><td style="padding: 0px;">&#64;</td><!-- blah! --><td style="padding: 0px;">&#110;</td><!-- blah! --><td style="padding: 0px;">&#117;</td><!-- blah! --><td style="padding: 0px;">&#108;</td><!-- blah! --><td style="padding: 0px;">&#108;</td><!-- blah! --><td style="padding: 0px;">&#46;</td><!-- blah! --><td style="padding: 0px;">&#99;</td><!-- blah! --><td style="padding: 0px;">&#111;</td><!-- blah! --><td style="padding: 0px;">&#109;</td><!-- blah! --></tr></table></a>')

		# invalid e-mail address (don't expect validation)
		self.assertEqual(common.obfusticate_email(''), '<a href="mailto:?subject=Saw%20your%20resume"><table style="border-spacing: 0px;"><tr></tr></table></a>')


	def test_format_year_from_string(self):
		"""test the format_year_from_string function"""

		self.assertEqual(common.format_year_from_string("2018-12-31"), '2018')
		self.assertEqual(common.format_year_from_string('18-12-31'), '0018')


	def test_format_month_year_from_string(self):
		"""test the format_month_year_from_string function"""

		self.assertEqual(common.format_month_year_from_string("2018-12-31"), 'December 2018')
		self.assertEqual(common.format_month_year_from_string('18-12-31'), 'December 0018')
		self.assertEqual(common.format_month_year_from_string("2000-01-31"), 'January 2000')


	def test_format_month_day_year_from_string(self):
		"""test the format_month_day_year_from_string function"""

		self.assertEqual(common.format_month_day_year_from_string("2018-12-31"), 'December 31, 2018')
		self.assertEqual(common.format_month_day_year_from_string('18-12-31'), 'December 31, 0018')
		self.assertEqual(common.format_month_day_year_from_string("2000-01-31"), 'January 31, 2000')
		self.assertEqual(common.format_month_day_year_from_string("2004-03-01"), 'March 01, 2004')


if __name__ == '__main__':
    unittest.main()