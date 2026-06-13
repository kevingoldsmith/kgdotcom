#!/usr/bin/env python
# *_* coding: utf-8 *_*

"""tests for the photos generator title resolution"""

import glob
import json
import os
import shutil
import tempfile
import unittest

from kgdotcom.generators.photos import Gallery, Image


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


def _find_source_jpg() -> str:
    """return a real jpg from the photos tree so tests have a loadable image"""
    for path in glob.glob("photos/**/*.jpg", recursive=True):
        return path
    return ""


class TestGalleryPreview(unittest.TestCase):
    """verify cover-image selection: newest by default, sidecar override by filename"""

    OLDER = "20200101-older.jpg"
    NEWER = "20240101-newer.jpg"

    def setUp(self) -> None:
        source = _find_source_jpg()
        if not source:
            self.skipTest("no source photo available")
        self.tmp = tempfile.mkdtemp()
        self.addCleanup(shutil.rmtree, self.tmp)
        shutil.copy(source, os.path.join(self.tmp, self.OLDER))
        shutil.copy(source, os.path.join(self.tmp, self.NEWER))

    def test_default_preview_is_newest(self) -> None:
        gallery = Gallery("TestGallery", self.tmp)
        gallery.populate()
        self.assertEqual(os.path.basename(gallery.preview_image.path), self.NEWER)

    def test_preview_override_by_filename(self) -> None:
        with open(
            os.path.join(self.tmp, "TestGallery.json"), "w", encoding="utf-8"
        ) as sidecar:
            json.dump({"preview": self.OLDER}, sidecar)
        gallery = Gallery("TestGallery", self.tmp)
        gallery.populate()
        self.assertEqual(os.path.basename(gallery.preview_image.path), self.OLDER)


if __name__ == "__main__":
    unittest.main()
