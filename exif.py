import datetime
from fractions import Fraction

from PIL import Image
import PIL.ExifTags


def process_exif_dict(exif_data_PIL):

    """
    Generate a dictionary of dictionaries.

    The outer dictionary keys are the names
    of individual items, eg Make, Model etc.

    The outer dictionary values are themselves
    dictionaries with the following keys:

        tag: the numeric code for the item names
        raw: the data as stored in the image, often
        in a non-human-readable format
        processed: the raw data if it is human-readable,
        or a processed version if not.
    """
    
    exif_data = {}

    for k, v in PIL.ExifTags.TAGS.items():

        if k in exif_data_PIL:
            value = exif_data_PIL[k]
            if len(str(value)) > 64:
                value = str(value)[:65] + "..."

            exif_data[v] = {"tag": k,
                            "raw": value,
                            "processed": value}

    exif_data = _process_exif_dict(exif_data)

    return exif_data


def _derationalize(rational):

    return rational.numerator / rational.denominator


def _create_lookups():

    lookups = {}

    lookups["metering_modes"] = ("Undefined",
                                 "Average",
                                 "Center-weighted average",
                                 "Spot",
                                 "Multi-spot",
                                 "Multi-segment",
                                 "Partial")

    lookups["exposure_programs"] = ("Undefined",
                                    "Manual",
                                    "Program AE",
                                    "Aperture-priority AE",
                                    "Shutter speed priority AE",
                                    "Creative (Slow speed)",
                                    "Action (High speed)",
                                    "Portrait ",
                                    "Landscape",
                                    "Bulb")

    lookups["resolution_units"] = ("",
                                   "Undefined",
                                   "Inches",
                                   "Centimetres")

    lookups["orientations"] = ("",
                               "Horizontal",
                               "Mirror horizontal",
                               "Rotate 180",
                               "Mirror vertical",
                               "Mirror horizontal and rotate 270 CW",
                               "Rotate 90 CW",
                               "Mirror horizontal and rotate 90 CW",
                               "Rotate 270 CW")

    return lookups


def _process_exif_dict(exif_dict):

    date_format = "%Y:%m:%d %H:%M:%S"

    lookups = _create_lookups()

    if "DateTime" in exif_dict:
        exif_dict["DateTime"]["processed"] = \
            datetime.datetime.strptime(exif_dict["DateTime"]["raw"], date_format)

    if "DateTimeOriginal" in exif_dict:
        exif_dict["DateTimeOriginal"]["processed"] = \
            datetime.datetime.strptime(exif_dict["DateTimeOriginal"]["raw"],
            date_format)
    if "DateTimeDigitized" in exif_dict:
        exif_dict["DateTimeDigitized"]["processed"] = \
            datetime.datetime.strptime(exif_dict["DateTimeDigitized"]["raw"], date_format)

    if "FNumber" in exif_dict:
        exif_dict["FNumber"]["processed"] = \
            _derationalize(exif_dict["FNumber"]["raw"])
        exif_dict["FNumber"]["processed"] = \
            "f{}".format(exif_dict["FNumber"]["processed"])
    
    if "MaxApertureValue" in exif_dict:
        exif_dict["MaxApertureValue"]["processed"] = \
            _derationalize(exif_dict["MaxApertureValue"]["raw"])
        exif_dict["MaxApertureValue"]["processed"] = \
            "f{:2.1f}".format(exif_dict["MaxApertureValue"]["processed"])

    if "FocalLength" in exif_dict:
        exif_dict["FocalLength"]["processed"] = \
            _derationalize(exif_dict["FocalLength"]["raw"])
        exif_dict["FocalLength"]["processed"] = \
            "{}mm".format(exif_dict["FocalLength"]["processed"])

    if "FocalLengthIn35mmFilm" in exif_dict:
        exif_dict["FocalLengthIn35mmFilm"]["processed"] = \
            "{}mm".format(exif_dict["FocalLengthIn35mmFilm"]["raw"])

    if "Orientation" in exif_dict:
        exif_dict["Orientation"]["processed"] = \
            lookups["orientations"][exif_dict["Orientation"]["raw"]]

    if "ResolutionUnit" in exif_dict:
        exif_dict["ResolutionUnit"]["processed"] = \
            lookups["resolution_units"][exif_dict["ResolutionUnit"]["raw"]]

    if "ExposureProgram" in exif_dict:
        exif_dict["ExposureProgram"]["processed"] = \
            lookups["exposure_programs"][exif_dict["ExposureProgram"]["raw"]]

    if "MeteringMode" in exif_dict:
        exif_dict["MeteringMode"]["processed"] = \
            lookups["metering_modes"][exif_dict["MeteringMode"]["raw"]]

    if "XResolution" in exif_dict:
        exif_dict["XResolution"]["processed"] = \
            int(_derationalize(exif_dict["XResolution"]["raw"]))
    
    if "YResolution" in exif_dict:
        exif_dict["YResolution"]["processed"] = \
            int(_derationalize(exif_dict["YResolution"]["raw"]))

    if "ExposureTime" in exif_dict:
        exif_dict["ExposureTime"]["processed"] = \
            _derationalize(exif_dict["ExposureTime"]["raw"])
        exif_dict["ExposureTime"]["processed"] = \
            str(Fraction(exif_dict["ExposureTime"]["processed"]).limit_denominator(8000))

    if "ExposureBiasValue" in exif_dict:
        exif_dict["ExposureBiasValue"]["processed"] = \
            _derationalize(exif_dict["ExposureBiasValue"]["raw"])
        exif_dict["ExposureBiasValue"]["processed"] = \
            "{} EV".format(exif_dict["ExposureBiasValue"]["processed"])

    # still need to process GPS, see https://stackoverflow.com/questions/19804768/interpreting-gps-info-of-exif-data-from-photo-in-python

    return exif_dict

# based on https://python.plainenglish.io/reading-a-photographs-exif-data-with-python-and-pillow-a29fceafb761