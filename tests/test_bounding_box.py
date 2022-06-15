import pytest

from geocoder_module.geocoder import Geocoder

geocoder = Geocoder()


class TestBoundingBoxIsLarge:
    async def test_bbox_is_large_x(self):
        bbox = [-178, 0, 178, 0]
        value = geocoder.check_large_bounding_box(bbox)
        assert value == True
        bbox = [178, 0, -178, 0]
        value = geocoder.check_large_bounding_box(bbox)
        assert value == True

    async def test_bbox_is_not_large_x(self):
        bbox = [-170, 0, 170, 0]
        value = geocoder.check_large_bounding_box(bbox)
        assert value == False
        bbox = [170, 0, -170, 0]
        value = geocoder.check_large_bounding_box(bbox)
        assert value == False

    async def test_bbox_is_large_y(self):
        bbox = [0, -178, 0, 178]
        value = geocoder.check_large_bounding_box(bbox)
        assert value == True
        bbox = [0, 178, 0, -178]
        value = geocoder.check_large_bounding_box(bbox)
        assert value == True

    async def test_bbox_is_not_large_y(self):
        bbox = [0, -170, 0, 170]
        value = geocoder.check_large_bounding_box(bbox)
        assert value == False
        bbox = [0, 170, 0, -170]
        value = geocoder.check_large_bounding_box(bbox)
        assert value == False
