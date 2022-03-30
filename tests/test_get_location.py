from unittest.mock import Mock, patch
import pytest

from geocoder_module.geocoder import Geocoder

geocoder = Geocoder()


@patch("requests.get")
def test_get_geocoder_info_returns_a_location_when_queried(
    mock_get,
):
    expected_get_geocoder_api_output = {
        "features": [
            {
                "geometry": {
                    "coordinates": [151.2164539, -33.8548157],
                    "type": "Point",
                },
                "type": "Feature",
                "properties": {
                    "osm_id": 5750005,
                    "osm_type": "R",
                    "extent": [150.260825, -33.3641481, 151.343898, -34.1732416],
                    "country": "Australia",
                    "osm_key": "place",
                    "countrycode": "AU",
                    "osm_value": "city",
                    "name": "Sydney",
                    "state": "New South Wales",
                    "type": "city",
                },
            },
            {
                "geometry": {"coordinates": [151.210047, -33.8679574], "type": "Point"},
                "type": "Feature",
                "properties": {
                    "osm_id": 5729534,
                    "osm_type": "R",
                    "extent": [151.1970047, -33.8561096, 151.223011, -33.8797564],
                    "country": "Australia",
                    "osm_key": "place",
                    "city": "Council of the City of Sydney",
                    "countrycode": "AU",
                    "osm_value": "suburb",
                    "postcode": "2000",
                    "name": "Sydney",
                    "state": "New South Wales",
                    "type": "district",
                },
            },
        ]
    }

    # Generate expected output from both get requests
    mock_get.return_value.json.return_value = expected_get_geocoder_api_output

    expected_output = [
        {
            "bounding_box": expected_get_geocoder_api_output["features"][0][
                "properties"
            ]["extent"],
            "name": expected_get_geocoder_api_output["features"][0]["properties"][
                "name"
            ],
            "country": expected_get_geocoder_api_output["features"][0]["properties"][
                "country"
            ],
            "coordinates": expected_get_geocoder_api_output["features"][0]["geometry"][
                "coordinates"
            ],
        }
    ]
    response = geocoder._get_geocode_info("sydney")

    assert mock_get.called
    assert response == expected_output


@patch("requests.get")
def test_get_geonames_info_returns_right_location_when_queried(
    mock_get,
):
    expected_get_geonames_api_output = {
        "name": "Sydney",
        "latitude": "-33.86778",
        "longitude": "151.20844",
        "country": "Australia",
        "continent": "Oceania",
    }
    # Generate expected output from both get requests
    mock_get.return_value.json.return_value = expected_get_geonames_api_output

    expected_output = [
        {
            "name": "Sydney",
            "coordinates": ["151.20844", "-33.86778"],
            "country": "Australia",
        }
    ]
    response = geocoder._get_geonames_info("sydney", "australia")

    assert mock_get.called
    assert response == expected_output


@patch("requests.get")
def test_get_location_info_returns_right_location_when_found_by_geocoder_and_geonames(
    mock_get,
):
    expected_get_geocoder_api_output = {
        "features": [
            {
                "geometry": {
                    "coordinates": [151.2164539, -33.8548157],
                    "type": "Point",
                },
                "type": "Feature",
                "properties": {
                    "osm_id": 5750005,
                    "osm_type": "R",
                    "extent": [150.260825, -33.3641481, 151.343898, -34.1732416],
                    "country": "Australia",
                    "osm_key": "place",
                    "countrycode": "AU",
                    "osm_value": "city",
                    "name": "Sydney",
                    "state": "New South Wales",
                    "type": "city",
                },
            },
        ]
    }
    expected_get_geonames_api_output = {
        "name": "Sydney",
        "latitude": "-33.86778",
        "longitude": "151.20844",
        "country": "Australia",
        "continent": "Oceania",
    }
    # Generate expected output from both get requests
    mock_get.return_value.json.return_value = "test"
    mock_get.return_value.json.side_effect = [
        expected_get_geocoder_api_output,
        expected_get_geonames_api_output,
    ]
    expected_output = [
        {
            "bounding_box": expected_get_geocoder_api_output["features"][0][
                "properties"
            ]["extent"],
            "name": expected_get_geocoder_api_output["features"][0]["properties"][
                "name"
            ],
            "country": expected_get_geocoder_api_output["features"][0]["properties"][
                "country"
            ],
            "coordinates": expected_get_geocoder_api_output["features"][0]["geometry"][
                "coordinates"
            ],
        }
    ]
    response = geocoder.get_location_info("sydney")

    assert mock_get.called
    assert response == expected_output


@patch("requests.get")
def test_get_location_info_returns_empty_list_when_location_found_by_geocoder_cant_be_validated_by_geonames(
    mock_get,
):
    expected_get_geocoder_api_output_2 = {
        "features": [
            {
                "geometry": {
                    "coordinates": [103.54583559171158, 1.3152402],
                    "type": "Point",
                },
                "type": "Feature",
                "properties": {
                    "osm_id": 412628254,
                    "osm_type": "W",
                    "extent": [103.5425018, 1.320748, 103.5483276, 1.3097538],
                    "country": "Malaysia",
                    "osm_key": "place",
                    "countrycode": "MY",
                    "osm_value": "island",
                    "name": "Asia Petroleum Hub",
                    "type": "locality",
                },
            }
        ]
    }
    expected_get_geonames_api_output_2 = {}
    # Generate expected output from both get requests
    mock_get.return_value.json.side_effect = [
        expected_get_geocoder_api_output_2,
        expected_get_geonames_api_output_2,
    ]
    expected_output = [{}]
    response = geocoder.get_location_info("asia petroleum hub")
    assert mock_get.called
    assert response == expected_output


@patch("requests.get")
def test_get_location_info_returns_empty_list_when_location_found_by_geocoder_cant_be_validated_by_geonames(
    mock_get,
):
    expected_get_geocoder_api_output_2 = {
        "features": [
            {
                "geometry": {
                    "coordinates": [103.54583559171158, 1.3152402],
                    "type": "Point",
                },
                "type": "Feature",
                "properties": {
                    "osm_id": 412628254,
                    "osm_type": "W",
                    "extent": [103.5425018, 1.320748, 103.5483276, 1.3097538],
                    "country": "Côte d'Ivoire",
                    "osm_key": "place",
                    "countrycode": "MY",
                    "osm_value": "island",
                    "name": "Côte d'Ivoire",
                    "type": "locality",
                },
            }
        ]
    }
    expected_get_geonames_api_output_2 = {}
    # Generate expected output from both get requests
    mock_get.return_value.json.side_effect = [
        expected_get_geocoder_api_output_2,
        expected_get_geonames_api_output_2,
    ]
    expected_output = [{}]
    response = geocoder.get_location_info("Côte d'Ivoire")
    assert mock_get.called
    assert response == expected_output
