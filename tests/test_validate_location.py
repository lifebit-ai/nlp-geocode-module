from unittest.mock import patch
import pytest
from tests.fixtures import *

from geocoder_module.geocoder import Geocoder

geocoder = Geocoder()

# Majority testing


class TestDoubleCheckCountries:
    @patch("geocoder_module.geocoder.Geocoder.get_location_info")
    def test_location_is_returned_valid_if_there_is_only_one_in_article(
        self,
        mock_get_location_info,
    ):
        locations = [
            location_output_old_paris,
        ]
        ner_tags = [ner_tag_paris, ner_tag_belgium]
        # Generate expected output from nlp-api response and add it to mock

        mock_get_location_info.return_value = [location_output_old_paris]

        # Get response
        response = geocoder.double_check_countries(locations, ner_tags)

        expected_output = [location_output_old_paris]

        assert response == expected_output

    @patch("geocoder_module.geocoder.Geocoder.get_location_info")
    def test_updated_location_is_returned_when_location_is_validated_with_others_in_article(
        self,
        mock_get_location_info,
    ):
        locations = [
            location_output_old_paris,
            location_output_san_antonio,
            location_output_texas,
        ]
        ner_tags = [ner_tag_paris, ner_tag_san_antonio, ner_tag_texas]
        # Generate expected output from nlp-api response and add it to mock

        mock_get_location_info.return_value = [location_output_new_paris]

        # Get response
        response = geocoder.double_check_countries(locations, ner_tags)

        expected_output = [
            location_output_new_paris,
            location_output_san_antonio,
            location_output_texas,
        ]

        assert response == expected_output

    @patch("geocoder_module.geocoder.Geocoder.get_location_info")
    def test_no_location_is_returned_when_locations_have_no_majority_no_ner_majority(
        self,
        mock_get_location_info,
    ):
        locations = [
            location_output_london_uk,
            location_output_san_antonio,
        ]
        ner_tags = []
        # Generate expected output from nlp-api response and add it to mock

        mock_get_location_info.return_value = [location_output_london_uk]

        # Get response
        response = geocoder.double_check_countries(locations, ner_tags)

        expected_output = [location_output_london_uk, location_output_san_antonio]

        assert response == expected_output

    def test_same_location_is_returned_when_location_is_same_than_others_in_article(
        self,
    ):

        locations = [
            location_output_san_antonio,
            location_output_texas,
        ]
        ner_tags = [ner_tag_san_antonio, ner_tag_texas]
        # Generate expected output from nlp-api response and add it to mock

        # Get response
        response = geocoder.double_check_countries(locations, ner_tags)

        expected_output = [
            location_output_san_antonio,
            location_output_texas,
        ]

        assert response == expected_output

    @patch("geocoder_module.geocoder.Geocoder.get_location_info")
    def test_updated_location_is_returned_when_location_is_same_than_others_in_article_and_only_1_reference_to_country(
        self,
        mock_get_location_info,
    ):
        ner_tags = [
            ner_tag_united_states,
            ner_tag_paris,
            ner_tag_san_antonio,
            ner_tag_texas,
        ]
        locations = [
            location_output_united_states,
            location_output_san_antonio,
            location_output_texas,
            location_output_old_paris,
        ]
        # Generate expected output from nlp-api response and add it to mock
        mock_get_location_info.return_value = [location_output_new_paris]
        # Get response
        response = geocoder.double_check_countries(locations, ner_tags)

        expected_output = [
            location_output_united_states,
            location_output_san_antonio,
            location_output_texas,
            location_output_new_paris,
        ]

        assert response == expected_output

    @patch("geocoder_module.geocoder.Geocoder.get_location_info")
    def test_discarded_location_when_location_is_not_in_countries_locations(
        self,
        mock_get_location_info,
    ):
        locations = [
            location_output_united_states,
            location_output_belgium,
            location_output_san_antonio,
            location_output_texas,
            location_output_old_paris,
        ]
        ner_tags = [
            ner_tag_united_states,
            ner_tag_belgium,
            ner_tag_paris,
            ner_tag_san_antonio,
            ner_tag_texas,
        ]
        # Generate expected output from nlp-api response and add it to mock
        mock_get_location_info.return_value = [location_output_old_paris]
        # Get response
        response = geocoder.double_check_countries(locations, ner_tags)

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
        self,
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
        ner_tags = [
            ner_tag_united_states,
            ner_tag_belgium,
            ner_tag_paris,
            ner_tag_san_antonio,
            ner_tag_texas,
            ner_tag_brussels,
        ]
        # Generate expected output from nlp-api response and add it to mock
        mock_get_location_info.return_value = [location_output_old_paris]
        # Get response
        response = geocoder.double_check_countries(locations, ner_tags)

        expected_output = [
            location_output_united_states,
            location_output_belgium,
            location_output_san_antonio,
            location_output_texas,
            {},
            location_output_brussels,
        ]

        assert response == expected_output

    @patch("geocoder_module.geocoder.Geocoder.get_location_info")
    def test_location_is_not_processed_if_no_country_key_in_location(
        self,
        mock_get_location_info,
    ):
        locations = [{}]
        ner_tags = [ner_tag_belgium, ner_tag_paris]
        # Create dummy return value, though this should not be called
        mock_get_location_info.json.return_value = "test"
        mock_get_location_info.json.side_effect = [ner_tag_belgium]
        # Get response
        response = geocoder.double_check_countries(locations, ner_tags)

        assert response == locations

    @patch("geocoder_module.geocoder.Geocoder.get_location_info")
    def test_location_is_not_processed_if_no_name_key_in_location(
        self,
        mock_get_location_info,
    ):
        locations = [
            {"country": "Spain", "bounding_box": [0, 0, 0, 0], "coodinates": [0, 0]}
        ]
        ner_tags = [ner_tag_belgium, ner_tag_paris]

        # Create dummy return value, though this should not be called
        mock_get_location_info.json.return_value = "test"
        mock_get_location_info.json.side_effect = [ner_tag_belgium]

        # Get response
        response = geocoder.double_check_countries(locations, ner_tags)

        # Expected output

        expected_output = [{}]

        assert response == expected_output

    @patch("geocoder_module.geocoder.Geocoder.get_location_info")
    def test_location_is_fixed_when_us_uk_problem_happens_and_reference_to_nation_in_tags(
        self,
        mock_get_location_info,
    ):

        locations = [
            location_output_london_us,
            location_output_twekesbury_uk,
            location_output_eastville_uk,
        ]
        ner_tags = [ner_tag_england]
        # Generate expected output from nlp-api response and add it to mock
        mock_get_location_info.return_value = [location_output_london_uk]
        # Get response
        response = geocoder.double_check_countries(locations, ner_tags)

        expected_output = [
            location_output_london_uk,
            location_output_twekesbury_uk,
            location_output_eastville_uk,
        ]

        assert response == expected_output

    @patch("geocoder_module.geocoder.Geocoder.get_location_info")
    def test_location_is_fixed_when_there_is_tie_and_country_reference_in_ner_tags(
        self,
        mock_get_location_info,
    ):

        locations = [
            location_output_london_us,
            location_output_crewe_us,
            location_output_twekesbury_uk,
            location_output_eastville_uk,
        ]
        ner_tags = [ner_tag_united_kingdom]
        # Generate expected output from nlp-api response and add it to mock

        mock_get_location_info.side_effect = [
            [location_output_united_kingdom],
            [location_output_london_uk],
            [location_output_crewe_uk],
            [location_output_london_uk],
            [location_output_crewe_uk],
        ]

        # Get response
        response = geocoder.double_check_countries(locations, ner_tags)

        expected_output = [
            location_output_london_uk,
            location_output_crewe_uk,
            location_output_twekesbury_uk,
            location_output_eastville_uk,
        ]

        assert response == expected_output


class TestFilterNerCountries:
    def test_filter_ner_tags_return_list_of_locations(self):
        ner_tags = [
            {"name": "Sidney", "label": "location"},
            {"name": "Australia", "label": "location"},
            {"name": "cow", "label": "host"},
        ]
        response_country, response_local = geocoder.filter_ner_countries(ner_tags)
        expected_countries = [{"name": "Australia", "label": "location"}]
        expected_local = [{"name": "Sidney", "label": "location"}]

        assert response_country == expected_countries
        assert response_local == expected_local

    def test_filter_ner_tags_return_empty_if_no_location(self):
        ner_tags = [
            {"name": "cow", "label": "host"},
        ]
        response_country, response_local = geocoder.filter_ner_countries(ner_tags)
        expected_countries = []
        expected_local = []

        assert response_country == expected_countries
        assert response_local == expected_local

    def test_filter_ner_tags_return_puerto_rico_as_local(self):
        ner_tags = [
            {"name": "Puerto Rico", "label": "location"},
            {"name": "Australia", "label": "location"},
            {"name": "cow", "label": "host"},
        ]
        response_country, response_local = geocoder.filter_ner_countries(ner_tags)
        expected_countries = [{"name": "Australia", "label": "location"}]
        expected_local = [{"name": "Puerto Rico", "label": "location"}]

        assert response_country == expected_countries
        assert response_local == expected_local


class TestCountCountries:
    def test_count_countries_when_country_given_and_no_top_countries(self):
        response = geocoder.count_countries(countries)
        expected_output = [("United Kingdom", 2), ("United States", 1)]
        assert response == expected_output

    def test_count_countries_when_country_and_top_countries_given(self):
        response = geocoder.count_countries(countries, 1)
        expected_output = [("United Kingdom", 2)]
        assert response == expected_output


class TestExtractCountries:
    def test_extract_countries_when_locations_contains_one_location_not_country(self):
        locations = [
            location_output_london_us,
        ]
        response_1, response_2, response_3 = geocoder.extract_countries(locations)

        expected_output_1 = ["United States"]
        expected_output_2 = {}
        expected_output_3 = {"London": "United States"}

        assert response_1 == expected_output_1
        assert response_2 == expected_output_2
        assert response_3 == expected_output_3

    def test_extract_countries_when_locations_contains_one_location_country(self):
        locations = [
            location_output_united_kingdom,
        ]
        response_1, response_2, response_3 = geocoder.extract_countries(locations)

        expected_output_1 = ["United Kingdom"]
        expected_output_2 = {"United Kingdom": 1}
        expected_output_3 = {"United Kingdom": "United Kingdom"}

        assert response_1 == expected_output_1
        assert response_2 == expected_output_2
        assert response_3 == expected_output_3

    def test_extract_countries_when_locations_contains_multiple_locations(self):
        locations = [
            location_output_london_us,
            location_output_crewe_us,
            location_output_twekesbury_uk,
            location_output_united_kingdom,
        ]
        response_1, response_2, response_3 = geocoder.extract_countries(locations)

        expected_output_1 = [
            "United States",
            "United States",
            "United Kingdom",
            "United Kingdom",
        ]
        expected_output_2 = {"United Kingdom": 1}
        expected_output_3 = {
            "London": "United States",
            "Crewe": "United States",
            "Twekesbury": "United Kingdom",
            "United Kingdom": "United Kingdom",
        }

        assert response_1 == expected_output_1
        assert response_2 == expected_output_2
        assert response_3 == expected_output_3


class TestCheckNewLocation:
    def test_return_new_locations_if_new_location_updated(self):
        new_location = [location_output_crewe_uk]
        response = geocoder.check_new_location(new_location, {}, {})

        assert response == new_location[0]

    def test_return_old_location_if_country_in_list_of_countries(self):
        location = location_output_crewe_uk
        only_countries = {"United Kingdom": 1}
        response = geocoder.check_new_location({}, location, only_countries)

        assert response == location

    def test_return_old_locations_if_not_list_of_old_countries(self):
        location = location_output_crewe_uk
        only_countries = {}
        response = geocoder.check_new_location({}, location, only_countries)

        assert response == location


class TestUpdateCountryForLocations:
    @patch("geocoder_module.geocoder.Geocoder.get_location_info")
    def test_returns_new_locations_list(self, mock_get_location_info):
        locations = [
            location_output_united_kingdom,
            location_output_london_us,
        ]
        mapping_countries = {
            "United Kingdom": "United Kingdom",
            "London": "United Kingdom",
        }
        only_countries = {"United Kingdom": 1}

        # Generate expected output from get_location_info response and add it to mock

        mock_get_location_info.side_effect = [[location_output_london_uk]]

        response = geocoder.update_country_for_locations(
            locations, mapping_countries, only_countries
        )
        expected_output = [location_output_united_kingdom, location_output_london_uk]

        assert response == expected_output

    @patch("geocoder_module.geocoder.Geocoder.get_location_info")
    def test_returns_new_locations_list(self, mock_get_location_info):
        locations = [
            location_output_united_kingdom,
            location_output_london_us,
        ]
        mapping_countries = {
            "United Kingdom": "United Kingdom",
            "London": "United Kingdom",
        }
        only_countries = {"United Kingdom": 1}

        # Generate expected output from get_location_info response and add it to mock

        mock_get_location_info.side_effect = [[location_output_london_uk]]

        response = geocoder.update_country_for_locations(
            locations, mapping_countries, only_countries
        )
        expected_output = [location_output_united_kingdom, location_output_london_uk]

        assert response == expected_output

    def test_returns_no_location_if_location_is_incomplete(self):
        locations = [
            location_output_united_kingdom,
        ]
        del locations[0]["name"]
        mapping_countries = {
            "United Kingdom": "United Kingdom",
        }
        only_countries = {"United Kingdom": 1}

        response = geocoder.update_country_for_locations(
            locations, mapping_countries, only_countries
        )
        expected_output = [{}]

        assert response == expected_output

    def test_returns_no_location_if_location_is_missing(self):
        locations = [{}]

        mapping_countries = {
            "United Kingdom": "United Kingdom",
        }
        only_countries = {"United Kingdom": 1}

        response = geocoder.update_country_for_locations(
            locations, mapping_countries, only_countries
        )
        expected_output = [{}]

        assert response == expected_output

    def test_returns_no_location_if_location_is_not_in_mapping_countries(self):
        locations = [
            location_output_london_uk,
        ]
        mapping_countries = {
            "United Kingdom": "United Kingdom",
        }
        only_countries = {"United Kingdom": 1}

        # Generate expected output from get_location_info response and add it to mock

        response = geocoder.update_country_for_locations(
            locations, mapping_countries, only_countries
        )
        expected_output = [{}]

        assert response == expected_output
