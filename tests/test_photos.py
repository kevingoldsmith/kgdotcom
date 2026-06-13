#!/usr/bin/env python
# *_* coding: utf-8 *_*

"""tests for the photos generator title resolution"""

import glob
import json
import os
import shutil
import tempfile
import unittest
from unittest import mock

from kgdotcom.generators.photos import (
    Gallery,
    Image,
    get_prev_next_nextnext,
)


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


class TestImageNavigation(unittest.TestCase):
    """prev/next navigation must follow the same newest-first order as the grid"""

    # created oldest-first on disk; expected display/nav order is newest-first
    NAMES = ["20200101-a.jpg", "20220101-b.jpg", "20240101-c.jpg"]

    def setUp(self) -> None:
        source = _find_source_jpg()
        if not source:
            self.skipTest("no source photo available")
        self.tmp = tempfile.mkdtemp()
        self.addCleanup(shutil.rmtree, self.tmp)
        for name in self.NAMES:
            shutil.copy(source, os.path.join(self.tmp, name))

    def _populate_oldest_first(self) -> Gallery:
        """populate with a deterministic oldest-first listdir order, so the test
        fails unless populate() explicitly sorts the images newest-first"""
        gallery = Gallery("TestGallery", self.tmp)
        with mock.patch(
            "kgdotcom.generators.photos.os.listdir", return_value=list(self.NAMES)
        ):
            gallery.populate()
        return gallery

    def test_images_sorted_newest_first(self) -> None:
        gallery = self._populate_oldest_first()
        order = [os.path.basename(img.path) for img in gallery.images]
        self.assertEqual(order, ["20240101-c.jpg", "20220101-b.jpg", "20200101-a.jpg"])

    def test_prev_next_follow_display_order(self) -> None:
        gallery = self._populate_oldest_first()
        # middle image is the 2022 one; in newest-first order its previous is
        # the newer 2024 image and its next is the older 2020 image
        middle = next(img for img in gallery.images if "20220101-b" in img.path)
        previous, next_image, _ = get_prev_next_nextnext(gallery.images, middle)
        self.assertEqual(os.path.basename(previous.path), "20240101-c.jpg")
        self.assertEqual(os.path.basename(next_image.path), "20200101-a.jpg")


if __name__ == "__main__":
    unittest.main()
