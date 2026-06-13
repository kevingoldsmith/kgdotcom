#!/usr/bin/env python
# *_* coding: utf-8 *_*

"""tests for the photos generator title resolution"""

import os
import unittest

from kgdotcom.generators.photos import Image


# example photos that carry their title only in a JSON sidecar (no embedded
# IPTC/EXIF/XMP title), used to guard against the gallery pages falling back
# to the filename instead of the sidecar title.
SIDECAR_EXAMPLES = [
    ("photos/UnitedStates/20260415-L1002961.jpg", "Monterrey, CA"),
    ("photos/UnitedStates/20240710-PXL_20240711.jpg", "Long Beach, Washington"),
]


class TestImageTitle(unittest.TestCase):
    """verify the resolved display title honors the JSON sidecar override"""

    def test_json_sidecar_title_resolved(self) -> None:
        for path, expected in SIDECAR_EXAMPLES:
            if not os.path.exists(path):
                self.skipTest(f"missing example photo: {path}")
            name = os.path.splitext(os.path.basename(path))[0]
            image = Image(name, path)
            self.assertEqual(image.title, expected)
            self.assertEqual(image.get_simple_metadata()["title"], expected)


if __name__ == "__main__":
    unittest.main()
