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
the merging of a subset of pairs of the bounding boxes
"""

PATH_SAMPLES = "tests/dummy_samples.json"
PATH_MERGED = "tests/dummy_merged.json"


def get_dummy_data(path):

    return json.load(open(path, "r"))


@mock.patch.dict(os.environ, {"PHOTON_SERVER": "http://0.0.0.0"})
def create_geocoder():

    return Geocoder()


@pytest.mark.parametrize(
    "name,bounding_box",
    [
        (sample["name"], sample["boundingBox"])
        for sample in get_dummy_data(PATH_SAMPLES)
    ],
)
def test_gps_sanity_check(name, bounding_box):
    """
    This function checks if the output of the
    gps_sanity_check for the input bounding box is
    in the correct format min_lon, min_lat, max_lon, max_lat
    """
    bbox = bounding_box[0] + bounding_box[1]
    assert bbox == gps_sanity_check(bbox)


@pytest.mark.parametrize(
    "name,bounding_box,edit_distance,editBoundingBoxAdd",
    [
        (
            sample["name"],
            sample["boundingBox"],
            sample["edit_distance"],
            sample["editBoundingBoxAdd"],
        )
        for sample in get_dummy_data(PATH_SAMPLES)
    ],
)
def test_edit_distance(name, bounding_box, edit_distance, editBoundingBoxAdd):
    """
    This function checks if changing the bounding box
    to a desired distance, that is the diagonal between the
    top left and the bottom right, is performed correctly
    """

    bounding_box = bounding_box[0] + bounding_box[1]
    edited_bounding_box = edit_bounding_box(bounding_box, edit_distance, add=True)
    assert editBoundingBoxAdd == edited_bounding_box


@pytest.mark.parametrize(
    "name,bounding_box,distance",
    [
        (
            sample["name"],
            sample["boundingBox"],
            sample["distance"],
        )
        for sample in get_dummy_data(PATH_SAMPLES)
    ],
)
def test_calculate_distance(name, bounding_box, distance):
    """
    This function checks if the distance between two
    point coordiantes is calculated correctly
    """

    assert distance == calculate_distance(bounding_box[0], bounding_box[1])


@pytest.mark.parametrize(
    "name,bounding_box,coordinates",
    [
        (
            sample["name"],
            sample["boundingBox"],
            sample["coordinates"],
        )
        for sample in get_dummy_data(PATH_SAMPLES)
    ],
)
def test_bbox2point_coord(name, bounding_box, coordinates):
    """
    This function checks if the conversion of a bounding box
    to a couple of GPS coordinates (a point coordinate) is
    performed correctly
    """

    bbox = bounding_box[0] + bounding_box[1]
    assert coordinates == bbox2point_coord(bbox)


@pytest.mark.parametrize(
    "first_name,second_name,merged,bbox1,bbox2",
    [
        (
            sample["first_name"],
            sample["second_name"],
            sample["merged"],
            sample["first_bbox"],
            sample["second_bbox"],
        )
        for sample in get_dummy_data(PATH_MERGED)
    ],
)
def test_merging_bbox(first_name, second_name, merged, bbox1, bbox2):
    """
    This function checks if the merging of two bounding boxes
    is performed correctly
    """
    geo = create_geocoder()

    assert merged == geo.merge_bounding_boxes([bbox1, bbox2])
