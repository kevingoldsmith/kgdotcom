#!/usr/bin/env python

import unittest
import navigation


class TestNavigation(unittest.TestCase):
    def test_get_href_root(self) -> None:
        """test get_href_root in module navigation"""
        self.assertEqual(navigation.get_href_root("index.html", True), "index.html")
        self.assertEqual(
            navigation.get_href_root("../index.html", True), "../index.html"
        )
        self.assertEqual(
            navigation.get_href_root("index.html", False), "https://kevingoldsmith.com/"
        )
        self.assertEqual(
            navigation.get_href_root("index.html"), "https://kevingoldsmith.com/"
        )
        # this is bogus as a corner case, but it is the expected behavior, we should fail if it changes
        self.assertEqual(
            navigation.get_href_root("../index.html", False),
            "https://kevingoldsmith.com/../",
        )

        self.assertEqual(navigation.get_href_root("resume.html", True), "resume.html")
        self.assertEqual(
            navigation.get_href_root("resume.html", False),
            "https://kevingoldsmith.com/resume.html",
        )

        self.assertEqual(
            navigation.get_href_root("talks/index.html", True), "talks/index.html"
        )
        self.assertEqual(
            navigation.get_href_root("talks/index.html", False),
            "https://kevingoldsmith.com/talks/",
        )

        self.assertEqual(
            navigation.get_href_root("index.html", True, True), "../index.html"
        )
        self.assertEqual(
            navigation.get_href_root("../index.html", True, True), "../../index.html"
        )
        self.assertEqual(
            navigation.get_href_root("index.html", False, True),
            "https://kevingoldsmith.com/",
        )
        # this is bogus as a corner case, but it is the expected behavior, we should fail if it changes
        self.assertEqual(
            navigation.get_href_root("../index.html", False, True),
            "https://kevingoldsmith.com/../",
        )

        self.assertEqual(
            navigation.get_href_root("resume.html", True, True), "../resume.html"
        )
        self.assertEqual(
            navigation.get_href_root("resume.html", False, True),
            "https://kevingoldsmith.com/resume.html",
        )

        self.assertEqual(
            navigation.get_href_root("talks/index.html", True, True),
            "../talks/index.html",
        )
        self.assertEqual(
            navigation.get_href_root("talks/index.html", False, True),
            "https://kevingoldsmith.com/talks/",
        )

    def test_get_talk_root_for_talk(self) -> None:
        """test get_talk_root_for_talk in module navigation"""
        self.assertEqual(navigation.get_talk_root_for_talk(True), "index.html")
        self.assertEqual(
            navigation.get_talk_root_for_talk(False),
            "https://kevingoldsmith.com/talks/",
        )
        self.assertEqual(
            navigation.get_talk_root_for_talk(), "https://kevingoldsmith.com/talks/"
        )

    def test_get_talk_url(self) -> None:
        """test get_talk_url function in module navigation"""
        self.assertEqual(
            navigation.get_talk_url("blah"), "https://kevingoldsmith.com/talks/blah"
        )
        self.assertEqual(
            navigation.get_talk_url("blah", False),
            "https://kevingoldsmith.com/talks/blah",
        )
        self.assertEqual(navigation.get_talk_url("blah", True), "blah")


if __name__ == "__main__":
    unittest.main()
