#!/usr/bin/env python
"""
    test the common module in the core package of kgdotcom
"""

import unittest
import os
from kgdotcom.core import common


class TestCommon(unittest.TestCase):
    """test the common module in the core package of kgdotcom"""

    def test_get_output_directory(self) -> None:
        """test the get_output_directory function"""

        # delete the directories if they are there?
        self.assertEqual(common.get_output_directory(True), "testoutput/")
        self.assertTrue(os.path.exists("testoutput/"))

        self.assertEqual(common.get_output_directory(False), "output/")
        self.assertTrue(os.path.exists("output/"))

    def test_obfusticate_email(self) -> None:
        """test the obfusticate_email function"""
        # valid e-mail address
        self.assertEqual(
            common.obfusticate_email("dev@null.com"),
            (
                '<a href="mailto:&#100;&#101;&#118;&#64;&#110;&#117;&#108;&#108;&#46;'
                + '&#99;&#111;&#109;?subject=Saw%20your%20resume"><table style="border-'
                + 'spacing: 0px;"><tr><td style="padding: 0px;">&#100;</td><!-- blah! -->'
                + '<td style="padding: 0px;">&#101;</td><!-- blah! --><td style="padding:'
                + ' 0px;">&#118;</td><!-- blah! --><td style="padding: 0px;">&#64;</td><!'
                + '-- blah! --><td style="padding: 0px;">&#110;</td><!-- blah! --><td style'
                + '="padding: 0px;">&#117;</td><!-- blah! --><td style="padding: 0px;">'
                + '&#108;</td><!-- blah! --><td style="padding: 0px;">&#108;</td><!-- blah!'
                + ' --><td style="padding: 0px;">&#46;</td><!-- blah! --><td style="'
                + 'padding: 0px;">&#99;</td><!-- blah! --><td style="padding: 0px;">&#111;'
                + '</td><!-- blah! --><td style="padding: 0px;">&#109;</td><!-- blah! -->'
                + "</tr></table></a>"
            ),
        )

        # invalid e-mail address (don't expect validation)
        self.assertEqual(
            common.obfusticate_email(""),
            (
                '<a href="mailto:?subject=Saw%20your%20resume"><table style="border'
                + '-spacing: 0px;"><tr></tr></table></a>'
            ),
        )

    def test_format_year_from_string(self) -> None:
        """test the format_year_from_string function"""

        self.assertEqual(common.format_year_from_string("2018-12-31"), "2018")
        self.assertEqual(common.format_year_from_string("18-12-31"), "0018")

    def test_format_month_year_from_string(self) -> None:
        """test the format_month_year_from_string function"""

        self.assertEqual(
            common.format_month_year_from_string("2018-12-31"), "December 2018"
        )
        self.assertEqual(
            common.format_month_year_from_string("18-12-31"), "December 0018"
        )
        self.assertEqual(
            common.format_month_year_from_string("2000-01-31"), "January 2000"
        )

    def test_format_month_day_year_from_string(self) -> None:
        """test the format_month_day_year_from_string function"""

        self.assertEqual(
            common.format_month_day_year_from_string("2018-12-31"), "December 31, 2018"
        )
        self.assertEqual(
            common.format_month_day_year_from_string("18-12-31"), "December 31, 0018"
        )
        self.assertEqual(
            common.format_month_day_year_from_string("2000-01-31"), "January 31, 2000"
        )
        self.assertEqual(
            common.format_month_day_year_from_string("2004-03-01"), "March 01, 2004"
        )

    def test_generate_paragraphs_for_lines(self) -> None:
        """test the generate_paragraphs_for_lines function"""

        self.assertEqual(
            common.generate_paragraphs_for_lines("i like cheese"), "i like cheese"
        )
        self.assertEqual(common.generate_paragraphs_for_lines(""), "")
        self.assertEqual(common.generate_paragraphs_for_lines(""), "")
        self.assertEqual(
            common.generate_paragraphs_for_lines("i like cheese\nand i cannot lie"),
            "<p>i like cheese</p>\n<p>and i cannot lie</p>\n",
        )
        self.assertEqual(common.generate_paragraphs_for_lines("\n"), "<p></p>\n")
        self.assertEqual(
            common.generate_paragraphs_for_lines("foo\nbar\nbaz"),
            "<p>foo</p>\n<p>bar</p>\n<p>baz</p>\n",
        )

    def test_format_city_state_country_from_location(self) -> None:
        """test the format_city_state_country_from_location function"""

        self.assertEqual(common.format_city_state_country_from_location({}), "virtual")
        self.assertEqual(
            common.format_city_state_country_from_location(
                {
                    "venue": "McCormick Place",
                    "address": "2301 S King Dr",
                    "city": "Chicago",
                    "state": "IL",
                    "country": "US",
                    "postal code": "60616",
                    "gps": [41.853306, -87.616059],
                }
            ),
            (
                '<span class="conferencecity">Chicago</span>, <span class='
                + '"conferenceState">IL</span>, <span class="conferencecountry">United'
                + " States</span>"
            ),
        )
        self.assertEqual(
            common.format_city_state_country_from_location(
                {
                    "venue": "MIC - Milano Convention Centre",
                    "address": "Piazzale Carlo Magno, 1",
                    "city": "Milano",
                    "state": "MI",
                    "country": "IT",
                    "postal code": "20149",
                    "gps": [45.480890, 9.153661],
                }
            ),
            (
                '<span class="conferencecity">Milano</span>, <span class='
                + '"conferenceState">MI</span>, <span class="conferencecountry">Italy'
                + "</span>"
            ),
        )
        self.assertEqual(
            common.format_city_state_country_from_location(
                {
                    "venue": "Valtech Stockholm",
                    "address": "Hantverkargatan 5",
                    "city": "Stockholm",
                    "country": "SE",
                    "postal code": "112 21",
                    "gps": [59.327917, 18.050547],
                }
            ),
            (
                '<span class="conferencecity">Stockholm</span>, <span '
                + 'class="conferencecountry">Sweden</span>'
            ),
        )

    def test_validate_url(self) -> None:
        """test URL validation"""
        self.assertFalse(common.validate_url("https://bla"))
        self.assertFalse(common.validate_url("https://qweqweqweqweqweq.qweqweqw.com"))
        self.assertTrue(common.validate_url("http://kevingoldsmith.com"))
        self.assertTrue(common.validate_url("https://cnn.com"))
        # test ignore list
        self.assertTrue(common.validate_url("https://devdays.lt/"))


if __name__ == "__main__":
    unittest.main()
