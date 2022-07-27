from unittest.mock import Mock, patch
import pytest

from geocoder_module.geocoder import Geocoder

geocoder = Geocoder()


class TestGetGeocoderInfo:
    @patch("requests.get")
    def test_returns_a_location_when_queried(
        self,
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
                    "geometry": {
                        "coordinates": [151.210047, -33.8679574],
                        "type": "Point",
                    },
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
                "country": expected_get_geocoder_api_output["features"][0][
                    "properties"
                ]["country"],
                "coordinates": expected_get_geocoder_api_output["features"][0][
                    "geometry"
                ]["coordinates"],
            }
        ]
        response = geocoder._get_geocode_info("sydney")

        assert mock_get.called
        assert response == expected_output

    @patch("requests.get")
    def test_returns_location_when_country_queried_but_result_has_no_extent(
        self, mock_get
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
                        "country": "Australia",
                        "osm_key": "place",
                        "countrycode": "AU",
                        "osm_value": "country",
                        "name": "Australia",
                        "type": "country",
                    },
                }
            ]
        }

        # Generate expected output from both get requests
        mock_get.return_value.json.return_value = expected_get_geocoder_api_output

        expected_output = [
            {
                "bounding_box": [72.2460938, -9.0882278, 168.2249543, -55.3228175],
                "name": expected_get_geocoder_api_output["features"][0]["properties"][
                    "name"
                ],
                "country": expected_get_geocoder_api_output["features"][0][
                    "properties"
                ]["country"],
                "coordinates": expected_get_geocoder_api_output["features"][0][
                    "geometry"
                ]["coordinates"],
            }
        ]
        response = geocoder._get_geocode_info("Australia")

        assert mock_get.called
        assert response == expected_output

    @patch("requests.get")
    def test_returns_empty_location_when_local_location_result_has_no_extent(
        self, mock_get
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
                        "country": "Australia",
                        "osm_key": "place",
                        "countrycode": "AU",
                        "osm_value": "country",
                        "name": "Sydney",
                        "type": "country",
                    },
                }
            ]
        }

        # Generate expected output from both get requests
        mock_get.return_value.json.return_value = expected_get_geocoder_api_output

        expected_output = []
        response = geocoder._get_geocode_info("Sydney")

        assert mock_get.called
        assert response == expected_output

    @patch("requests.get")
    def test_returns_right_location_when_country_queried_with_country_field_but_result_has_no_extent(
        self, mock_get
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
                        "country": "Australia",
                        "osm_key": "place",
                        "countrycode": "AU",
                        "osm_value": "country",
                        "name": "Australia",
                        "type": "country",
                    },
                }
            ]
        }

        # Generate expected output from both get requests
        mock_get.return_value.json.return_value = expected_get_geocoder_api_output

        expected_output = [
            {
                "bounding_box": [72.2460938, -9.0882278, 168.2249543, -55.3228175],
                "name": expected_get_geocoder_api_output["features"][0]["properties"][
                    "name"
                ],
                "country": expected_get_geocoder_api_output["features"][0][
                    "properties"
                ]["country"],
                "coordinates": expected_get_geocoder_api_output["features"][0][
                    "geometry"
                ]["coordinates"],
            }
        ]
        response = geocoder._get_geocode_info("Australia", country="Australia")

        assert mock_get.called
        assert response == expected_output


class TestGetGeonames:
    @patch("requests.get")
    def test_get_geonames_info_returns_right_location_when_queried(
        self,
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


class TestGetLocationInfo:
    @patch("requests.get")
    def test_get_location_info_returns_right_location_when_found_by_geocoder_and_geonames(
        self,
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
                "country": expected_get_geocoder_api_output["features"][0][
                    "properties"
                ]["country"],
                "coordinates": expected_get_geocoder_api_output["features"][0][
                    "geometry"
                ]["coordinates"],
            }
        ]
        response = geocoder.get_location_info("sydney")

        assert mock_get.called
        assert response == expected_output

    @patch("requests.get")
    def test_get_location_info_returns_empty_list_when_location_found_by_geocoder_cant_be_validated_by_geonames(
        self,
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
        expected_output = []
        response = geocoder.get_location_info("asia petroleum hub")
        assert mock_get.called
        assert response == expected_output


class TestValidateLocations:
    @patch("requests.get")
    def test_returns_validated_location(self, mock_get):
        expected_output = []
        expected_get_geonames_api_output = {
            "name": "Sydney",
            "latitude": "-33.86778",
            "longitude": "151.20844",
            "country": "Australia",
            "continent": "Oceania",
        }
        mock_get.return_value.json = expected_get_geonames_api_output
        response = geocoder._validate_locations(
            [{"name": "Sydney", "country": "Australia"}], "Sydney"
        )
        assert response == expected_output

    @patch("requests.get")
    def test_returns_empty_value_when_given_empty_value(self, mock_get):
        expected_output = []
        expected_get_geonames_api_output = {}
        mock_get.return_value.json = expected_get_geonames_api_output
        response = geocoder._validate_locations(
            [{"name": "Paris", "country": "Poland"}], "Paris"
        )
        assert response == expected_output

    def test_return_empty_value_when_given_wrong_value(self):
        expected_output = []
        response = geocoder._validate_locations([], "Paris")
        assert response == expected_output


class TestBlacklist:
    def test_get_location_blacklist_returns_empty_location(self):
        for i in geocoder.config["blacklist"]:
            response = geocoder.get_location_info(i)
            assert response == []


class TestHandleAcronyms:
    def test_no_duplicates_in_country_acronyms(self):
        for key in geocoder.country_acronyms:
            for acronym in geocoder.country_acronyms[key]:
                counter = 0
                for key_two in geocoder.country_acronyms:
                    if acronym in geocoder.country_acronyms[key_two]:
                        counter += 1
                print(acronym)
                assert counter == 1

    def test_acronym_is_found_and_normalised(self):
        response = geocoder._handle_acronyms("UK")
        assert response == "united kingdom"
        response = geocoder._handle_acronyms("US")
        assert response == "united states"
        response = geocoder._handle_acronyms("Us")
        assert response == "Us"
        response = geocoder._handle_acronyms("U.S")
        assert response == "united states"
        response = geocoder._handle_acronyms("\u65b0\u52a0\u5761")
        assert response == "singapore"

    def test_country_location_is_returned_untouched(self):
        response = geocoder._handle_acronyms("united kingdom")
        assert response == "united kingdom"

    def test_local_location_is_returned_untouched(self):
        response = geocoder._handle_acronyms("madrid")
        assert response == "madrid"

    class TestReverseEndpoint:
        @patch("requests.get")
        def test_get_hit_from_coordinates(self, mock_get):
            latitude = -33.8548157
            longitude = 151.2164539
            expected_get_reverse_api_output = {
                "features": [
                    {
                        "geometry": {
                            "coordinates": [151.01319457370295, -32.98035125],
                            "type": "Point",
                        },
                        "type": "Feature",
                        "properties": {
                            "osm_id": 5750005,
                            "osm_type": "R",
                            "extent": [
                                150.260825,
                                -33.3641481,
                                151.343898,
                                -34.1732416,
                            ],
                            "country": "Australia",
                            "osm_key": "place",
                            "countrycode": "AU",
                            "osm_value": "city",
                            "name": "Cessnock City Council",
                            "city": "Cessnock City Council",
                            "state": "New South Wales",
                            "type": "city",
                        },
                    },
                ]
            }

            mock_get.return_value.json.return_value = expected_get_reverse_api_output

            expected_output = {
                "city": "Cessnock City Council",
                "country": "Australia",
                "coordinates": [151.01319457370295, -32.98035125],
                "bounding_box": [
                    150.74517472942034,
                    -32.75552084852031,
                    151.28121441798555,
                    -33.205181651479684,
                ],
            }
            response = geocoder.get_location_from_coordinates(latitude, longitude)

            assert mock_get.called
            assert response == expected_output

        @patch("requests.get")
        def test_get_no_result_from_coordinates(self, mock_get):
            latitude = 80.8548157
            longitude = 151.2164539
            expected_get_reverse_api_output = {"features": [{}]}

            mock_get.return_value.json.return_value = expected_get_reverse_api_output

            expected_output = {}
            response = geocoder.get_location_from_coordinates(latitude, longitude)

            assert mock_get.called
            assert response == expected_output
