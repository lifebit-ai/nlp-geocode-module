import pytest

from geocoder_module.geocoder import Geocoder

geocoder = Geocoder()


class TestBoundingBoxIsLarge:
    def test_bbox_is_large_x(self):
        bbox = [-178, 0, 178, 0]
        value = geocoder.check_large_bounding_box(bbox)
        assert value == True
        bbox = [178, 0, -178, 0]
        value = geocoder.check_large_bounding_box(bbox)
        assert value == True

    def test_bbox_is_not_large_x(self):
        bbox = [-170, 0, 170, 0]
        value = geocoder.check_large_bounding_box(bbox)
        assert value == False
        bbox = [170, 0, -170, 0]
        value = geocoder.check_large_bounding_box(bbox)
        assert value == False

    def test_bbox_is_large_y(self):
        bbox = [0, -178, 0, 178]
        value = geocoder.check_large_bounding_box(bbox)
        assert value == True
        bbox = [0, 178, 0, -178]
        value = geocoder.check_large_bounding_box(bbox)
        assert value == True

    def test_bbox_is_not_large_y(self):
        bbox = [0, -170, 0, 170]
        value = geocoder.check_large_bounding_box(bbox)
        assert value == False
        bbox = [0, 170, 0, -170]
        value = geocoder.check_large_bounding_box(bbox)
        assert value == False

    def test_bbox_single_x_is_large(self):
        bbox = [-180, 0, 0, 0]
        value = geocoder.check_large_bounding_box(bbox)
        assert value == False
        bbox = [180, 0, 0, 0]
        value = geocoder.check_large_bounding_box(bbox)
        assert value == False
        bbox = [0, 0, -180, 0]
        value = geocoder.check_large_bounding_box(bbox)
        assert value == False
        bbox = [0, 0, 180, 0]
        value = geocoder.check_large_bounding_box(bbox)
        assert value == False

    def test_bbox_single_x_is_not_large(self):
        bbox = [-160, 0, 0, 0]
        value = geocoder.check_large_bounding_box(bbox)
        assert value == False
        bbox = [160, 0, 0, 0]
        value = geocoder.check_large_bounding_box(bbox)
        assert value == False
        bbox = [0, 0, -160, 0]
        value = geocoder.check_large_bounding_box(bbox)
        assert value == False
        bbox = [0, 0, 160, 0]
        value = geocoder.check_large_bounding_box(bbox)
        assert value == False

    def test_bbox_single_y_is_large(self):
        bbox = [0, -180, 0, 0]
        value = geocoder.check_large_bounding_box(bbox)
        assert value == False
        bbox = [0, 180, 0, 0]
        value = geocoder.check_large_bounding_box(bbox)
        assert value == False
        bbox = [0, 0, 0, -180]
        value = geocoder.check_large_bounding_box(bbox)
        assert value == False
        bbox = [0, 0, 0, 180]
        value = geocoder.check_large_bounding_box(bbox)
        assert value == False

    def test_bbox_single_y_is_not_large(self):
        bbox = [0, -160, 0, 0]
        value = geocoder.check_large_bounding_box(bbox)
        assert value == False
        bbox = [0, 160, 0, 0]
        value = geocoder.check_large_bounding_box(bbox)
        assert value == False
        bbox = [0, 0, 0, -160]
        value = geocoder.check_large_bounding_box(bbox)
        assert value == False
        bbox = [0, 0, 0, 160]
        value = geocoder.check_large_bounding_box(bbox)
        assert value == False
