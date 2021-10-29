import os
import json
import pytest
from unittest import mock
from geocoder_module.geocoder import Geocoder
from geocoder_module.utils import (
    bbox2point_coord,
    calculate_distance,
    edit_bounding_box,
    gps_sanity_check,
)


"""
This dummy data is composed by random capitals from which gps
coordinates are extracted. The results of edit function and
distances is attached to them, while the merged samples are
the marging of all the pairs of the bounding boxes
"""

PATH_SAMPLES = "tests/dummy_samples.json"
PATH_MERGED = "tests/dummy_merged.json"


def get_dummy_data(path):

    return json.load(open(path, "r"))


@mock.patch.dict(os.environ, {"PHOTON_SERVER": "http://0.0.0.0"})
def create_geocoder():

    return Geocoder()


def test_gps_sanity_check():
    """
    This function checks if the output of the
    gps_sanity_check for the input bounding box is
    in the correct format min_lon, min_lat, max_lon, max_lat
    """

    dummy_samples = get_dummy_data(PATH_SAMPLES)

    for sample in dummy_samples:
        bounding_box = sample["boundingBox"][0] + sample["boundingBox"][1]
        assert bounding_box == gps_sanity_check(bounding_box)


def test_bbox2point_coord():
    """
    This function checks if the conversion of a bounding box
    to a couple of GPS coordinates (a point coordinate) is
    performed correctly
    """

    dummy_samples = get_dummy_data(PATH_SAMPLES)

    for sample in dummy_samples:
        bounding_box = sample["boundingBox"][0] + sample["boundingBox"][1]
        assert sample["coordinates"] == bbox2point_coord(bounding_box)


def test_calculate_distance():
    """
    This function checks if the distance between two
    point coordiantes is calculated correctly
    """

    dummy_samples = get_dummy_data(PATH_SAMPLES)

    for sample in dummy_samples:
        distance = calculate_distance(
            sample["boundingBox"][0], sample["boundingBox"][1]
        )
        assert distance == sample["distance"]


def test_edit_distance():
    """
    This function checks if changing the bounding box
    to a desired distance, that is the diagonal between the
    top left and the bottom right, is performed correctly
    """

    dummy_samples = get_dummy_data(PATH_SAMPLES)

    for sample in dummy_samples:
        bounding_box = sample["boundingBox"][0] + sample["boundingBox"][1]
        edited_bounding_box = edit_bounding_box(
            bounding_box, sample["edit_distance"], add=True
        )
        assert sample["editBoundingBoxAdd"] == edited_bounding_box


def test_merging_bounding_boxes():
    """
    This function checks if merging two bounding boxes
    results in the correct fineal bounding box, as per
    the provided samples
    """

    dummy_merged = get_dummy_data(PATH_MERGED)
    geo = create_geocoder()

    for sample in dummy_merged:
        merged = geo.merge_bounding_boxes([sample["first"], sample["second"]])
        assert merged == sample["merged"]
