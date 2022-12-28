import datetime

import typing
from fractions import Fraction
from PIL import Image
from PIL.Image import Exif
from PIL.ExifTags import GPSTAGS, TAGS
from PIL.TiffImagePlugin import IFDRational


def get_exif_data(image:Image.Image) -> Exif:

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
    
    exif_data:Exif = image.getexif()

    for k, v in TAGS.items():
        if v == "ExifOffset":
            info = exif_data.get_ifd(k)
            for k2, v2 in info.items():
                k2_tag = TAGS.get(k2,k2)
                exif_data[k2_tag] = {
                    "tag": k2_tag,
                    "raw": v2,
                    "processed": v2
                }
        elif k in exif_data:
            value = exif_data[k]
            if len(str(value)) > 64:
                value = str(value)[:65] + "..."

            exif_data[v] = {"tag": k,
                            "raw": value,
                            "processed": value}

    exif_data = _process_exif_dict(exif_data)

    return exif_data


def _derationalize(rational: IFDRational) -> float:

    return rational.numerator / rational.denominator


def _create_lookups() -> dict:

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


def dms_to_degrees(v: typing.Any) -> float:
    """Convert degree/minute/second to decimal degrees."""

    if IFDRational and isinstance(v[0], IFDRational):
        d = float(v[0])
        m = float(v[1])
        s = float(v[2])
    else:
        d = float(v[0][0]) / float(v[0][1])
        m = float(v[1][0]) / float(v[1][1])
        s = float(v[2][0]) / float(v[2][1])
    return d + (m / 60.0) + (s / 3600.0)


def _process_exif_dict(exif_dict: Exif) -> Exif:

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

    if "GPSInfo" in exif_dict:
        if exif_dict["GPSInfo"]["raw"] is not dict:
            exif_dict["GPSInfo"]["raw"] = exif_dict.get_ifd(exif_dict["GPSInfo"]["tag"])
        exif_dict["GPSInfo"]["processed"] = {
            GPSTAGS.get(tag, tag): value for tag, value in exif_dict["GPSInfo"]["raw"].items()
        }
        lat_info = exif_dict["GPSInfo"]["processed"].get('GPSLatitude')
        lon_info = exif_dict["GPSInfo"]["processed"].get('GPSLongitude')
        lat_ref_info = exif_dict["GPSInfo"]["processed"].get('GPSLatitudeRef')
        lon_ref_info = exif_dict["GPSInfo"]["processed"].get('GPSLongitudeRef')

        if lat_info and lon_info and lat_ref_info and lon_ref_info:
            try:
                lat = dms_to_degrees(lat_info)
                lon = dms_to_degrees(lon_info)
            except (ZeroDivisionError, ValueError, TypeError):
                pass
            else:
                exif_dict["GPSInfo"]["processed"]["simpleGPS"] = {
                    'lat': -lat if lat_ref_info != 'N' else lat,
                    'lon': -lon if lon_ref_info != 'E' else lon,
                }

    return exif_dict

# based on https://python.plainenglish.io/reading-a-photographs-exif-data-with-python-and-pillow-a29fceafb761