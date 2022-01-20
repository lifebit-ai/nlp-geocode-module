from unittest.mock import Mock, patch
import pytest

from geocoder_module.geocoder import Geocoder

geocoder = Geocoder()

location_output_brussels = {
    "name": "Brussels",
    "bounding_box": [2.224122, 48.902156, 2.4697602, 48.8155755],
    "country": "Belgium",
    "coordinates": [2.3514616, 48.8566969],
}

location_output_belgium = {
    "name": "Belgium",
    "bounding_box": [-98.8131865, 29.7309623, -98.2230029, 29.1862572],
    "country": "Belgium",
    "coordinates": [-98.4951405, 29.4246002],
}

location_output_united_states = {
    "name": "United States",
    "bounding_box": [-98.8131865, 29.7309623, -98.2230029, 29.1862572],
    "country": "United States",
    "coordinates": [-98.4951405, 29.4246002],
}

location_output_old_paris = {
    "name": "Paris",
    "bounding_box": [2.224122, 48.902156, 2.4697602, 48.8155755],
    "country": "France",
    "coordinates": [2.3514616, 48.8566969],
}
location_output_new_paris = {
    "name": "Paris",
    "bounding_box": [-95.6279396, 33.7383866, -95.4354115, 33.6206345],
    "country": "United States",
    "coordinates": [-95.555513, 33.6617962],
}
location_output_san_antonio = {
    "name": "San Antonio",
    "bounding_box": [-98.8131865, 29.7309623, -98.2230029, 29.1862572],
    "country": "United States",
    "coordinates": [-98.4951405, 29.4246002],
}
location_output_texas = {
    "name": "Texas",
    "bounding_box": [-106.6458459, 36.5004529, -93.5078217, 25.83706],
    "country": "United States",
    "coordinates": [-99.5120986, 31.8160381],
}


@patch("geocoder_module.geocoder.Geocoder.get_location_info")
def test_location_is_returned_valid_if_there_is_only_one_in_article(
    mock_get_location_info,
):
    locations = [
        location_output_old_paris,
    ]
    # Generate expected output from nlp-api response and add it to mock

    mock_get_location_info.return_value = [location_output_old_paris]

    # Get response
    response = geocoder.double_check_countries(locations)

    expected_output = [location_output_old_paris]

    assert response == expected_output


@patch("geocoder_module.geocoder.Geocoder.get_location_info")
def test_updated_location_is_returned_when_location_is_validated_with_others_in_article(
    mock_get_location_info,
):
    locations = [
        location_output_old_paris,
        location_output_san_antonio,
        location_output_texas,
    ]
    # Generate expected output from nlp-api response and add it to mock

    mock_get_location_info.return_value = [location_output_new_paris]

    # Get response
    response = geocoder.double_check_countries(locations)

    expected_output = [
        location_output_new_paris,
        location_output_san_antonio,
        location_output_texas,
    ]

    assert response == expected_output


def test_same_location_is_returned_when_location_is_same_than_others_in_article():

    locations = [
        location_output_san_antonio,
        location_output_texas,
    ]
    # Generate expected output from nlp-api response and add it to mock

    # Get response
    response = geocoder.double_check_countries(locations)

    expected_output = [
        location_output_san_antonio,
        location_output_texas,
    ]

    assert response == expected_output


@patch("geocoder_module.geocoder.Geocoder.get_location_info")
def test_updated_location_is_returned_when_location_is_same_than_others_in_article_and_only_1_reference_to_country(
    mock_get_location_info,
):

    locations = [
        location_output_united_states,
        location_output_san_antonio,
        location_output_texas,
        location_output_old_paris,
    ]
    # Generate expected output from nlp-api response and add it to mock
    mock_get_location_info.return_value = [location_output_new_paris]
    # Get response
    response = geocoder.double_check_countries(locations)

    expected_output = [
        location_output_united_states,
        location_output_san_antonio,
        location_output_texas,
        location_output_new_paris,
    ]

    assert response == expected_output


@patch("geocoder_module.geocoder.Geocoder.get_location_info")
def test_discarded_location_when_location_is_not_in_countries_locations(
    mock_get_location_info,
):
    locations = [
        location_output_united_states,
        location_output_belgium,
        location_output_san_antonio,
        location_output_texas,
        location_output_old_paris,
    ]
    # Generate expected output from nlp-api response and add it to mock
    mock_get_location_info.return_value = [location_output_old_paris]
    # Get response
    response = geocoder.double_check_countries(locations)

    expected_output = [
        location_output_united_states,
        location_output_belgium,
        location_output_san_antonio,
        location_output_texas,
        {},
    ]

    assert response == expected_output


@patch("geocoder_module.geocoder.Geocoder.get_location_info")
def test_retain_all_locations_in_country_when_location_is_in_countries_location(
    mock_get_location_info,
):

    locations = [
        location_output_united_states,
        location_output_belgium,
        location_output_san_antonio,
        location_output_texas,
        location_output_old_paris,
        location_output_brussels,
    ]
    # Generate expected output from nlp-api response and add it to mock
    mock_get_location_info.return_value = [location_output_old_paris]
    # Get response
    response = geocoder.double_check_countries(locations)

    expected_output = [
        location_output_united_states,
        location_output_belgium,
        location_output_san_antonio,
        location_output_texas,
        {},
        location_output_brussels,
    ]

    assert response == expected_output
