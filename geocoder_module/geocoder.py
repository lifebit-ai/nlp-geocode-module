import json
import sys
import os
from typing import Any, Dict, List, Tuple
from collections import Counter
import requests
from logger.logging import logging


import geocoder_module
from geocoder_module.utils import (
    calculate_distance,
    edit_bounding_box,
    gps_sanity_check,
    bbox2point_coord,
)

_wrap_latitude = lambda x: x + 90


class Geocoder:
    def __init__(self) -> None:
        """
        This class creates the Geocoder module, that is an object
        to get coordinates from the normalised name of a location,
        alongside with its country and the bounding box coordinates
        of its area (top left corner and bottom right corner).
        The object is an interface to the Photon geocoder; its entrypoint
        has to be provided in the config file.

        :param config: string path for the config file
        """

        self.config = {
            "geonames_api_endpoint": "/locations/?",
            "url_api_endpoint": "/api?",
            "url_reverse_endpoint": "/reverse?",
            "lang": "en",
            "osm_keys": "place",
            "country_neighbors_path": "country_neighbors.json",
            "country_bounding_box_path": "countries_bbox.json",
            "blacklist": open(
                os.path.join(
                    os.path.dirname(os.path.dirname(geocoder_module.__file__)),
                    "geocoder_module",
                    "blacklist.txt",
                ),
                "r",
            ).readlines(),
        }

        try:
            self.map_country_neighbors = json.load(
                open(
                    os.path.join(
                        os.path.dirname(os.path.dirname(geocoder_module.__file__)),
                        "geocoder_module",
                        self.config["country_neighbors_path"],
                    ),
                    "r",
                )
            )
        except:
            logging.error(
                "The json file {} specified in the configuration can't be read.".format(
                    self.config["country_neighbors_path"]
                )
            )
        try:
            self.country_bbox = json.load(
                open(
                    os.path.join(
                        os.path.dirname(os.path.dirname(geocoder_module.__file__)),
                        "geocoder_module",
                        self.config["country_bounding_box_path"],
                    ),
                    "r",
                )
            )
        except:
            logging.error(
                "The json file {} specified in the configuration can't be read.".format(
                    self.config["country_bounding_box_path"]
                )
            )

        try:
            print("Using Photon Geocoder server on: " + os.environ["PHOTON_SERVER"])
        except:
            logging.error(
                "The environment variable PHOTON_SERVER has not been specified"
            )
            sys.exit(-1)

        try:
            print("Using Geonames server on: " + os.environ["GEONAMES_SERVER"])
        except:
            logging.error(
                "The environment variable GEONAMES_SERVER has not been specified"
            )
            sys.exit(-1)

    def _get_geonames_info(self, location: str, country: str) -> List[Dict[str, any]]:
        """
        This function returns a list of dictionaries representing the
        geographical information of the normalized location passed in input.
        The resulting dictionaries are composed of a normalized name (field "name"),
        four gps coordinates of the two corners of its bounding box if the location is a country (field "extent"),
        the country where it belongs (field "country"), and the gps coordinates,
        longitude and latitude (field "coordinates").
        The paramter country specifies the country where to search in for the
        given location.

        :param location:       string that represents the location to query for

        :param country:        string that represents the country where to search
                               the input location
        """
        try:
            url_api = (
                os.environ["GEONAMES_SERVER"] + self.config["geonames_api_endpoint"]
            )

            response = requests.get(
                url_api,
                params={"country": country.lower(), "local_location": location.lower()},
            )
            response = response.json()
        except Exception as e:
            logging.error("Error in querying location {} ".format(location))
            logging.error(e)
        results = []
        # Create location object with results
        location = {}
        if "name" in response:
            location["name"] = response["name"]
            location["country"] = response["country"]
            location["coordinates"] = [response["longitude"], response["latitude"]]
            if location["name"].lower() == country.lower():
                try:
                    location["bounding_box"] = self.country_bbox[country.lower()]
                except:
                    location["bounding_box"] = []
            results.append(location)
        return results

    def _get_geocode_info(
        self, location: str, best_matching: bool = True, country: str = None
    ) -> List[Dict[str, any]]:
        """
        This function returns a list of dictionaries representing the
        geographical information of the normalized location passed in input.
        The resulting dictionaries are composed of a normalized name (field "name"),
        four gps coordinates of the two corners of its bounding box (field "extent"),
        the country where it belongs (field "country"), and the gps coordinates,
        longitude and latitude (field "coordinates").
        The best_matching parameter is used to specify if the method will return
        only the first result or all the results obtained querying Photon.
        The paramter country specifies the country where to search in for the
        given location.

        :param location:       string that represents the location to query for
        :param best_matching:  bool, if True the first results is returend,
                               otherwise all the results are returned
                               (default True)
        :param country:        string that represents the country where to search
                               the input location (default None)
        """
        try:
            url_api = os.environ["PHOTON_SERVER"] + self.config["url_api_endpoint"]

            response = requests.get(
                url_api,
                params={
                    "q": location,
                    "lang": self.config["lang"],
                    "osm_tag": self.config["osm_keys"],
                },
            )
            response = response.json()
        except Exception as e:
            logging.error(f"Error in querying location {location} : {e}")

        results = []

        for i in range(len(response["features"])):
            location = {}
            features = response["features"][i]

            # avoid data with missing fields
            if not "name" in features["properties"].keys():
                continue
            if not "extent" in features["properties"].keys():
                continue
            if not "country" in features["properties"].keys():
                continue
            if not "coordinates" in features["geometry"].keys():
                continue

            # check if a country is provided and filter other locations
            if country and features["properties"]["country"] != country:
                continue

            # If the location queried is a country,
            # then retrieve the bounding box from countries_bbox.json
            if (
                features["properties"]["name"].lower()
                == features["properties"]["country"].lower()
            ):
                location["bounding_box"] = self.country_bbox[
                    features["properties"]["country"].lower()
                ]
            else:
                location["bounding_box"] = features["properties"]["extent"]

            location["name"] = features["properties"]["name"]
            location["country"] = features["properties"]["country"]
            location["coordinates"] = features["geometry"]["coordinates"]

            # Add results
            results.append(location)

            # the first results is the always the best matching one
            if best_matching:
                break

        return results

    def get_location_info(
        self, location: str, best_matching: bool = True, country: str = None
    ) -> List[Dict[str, any]]:
        """
        This function returns a list of dictionaries representing the
        geographical information of the normalized location passed in input.
        The resulting dictionaries are composed of a normalized name (field "name"),
        four gps coordinates of the two corners of its bounding box (field "extent"),
        the country where it belongs (field "country"), and the gps coordinates,
        longitude and latitude (field "coordinates").
        The best_matching parameter is used to specify if the method will return
        only the first result or all the results obtained querying Photon.
        The paramter country specifies the country where to search in for the
        given location.

        :param location:       string that represents the location to query for
        :param best_matching:  bool, if True the first results is returend,
                               otherwise all the results are returned
                               (default True)
        :param country:        string that represents the country where to search
                               the input location (default None)
        """
        # Check that location is not in blacklist
        if location.lower() in self.config["blacklist"]:
            logging.warning(
                f"Location is in blacklist: {location}. Returning empty location"
            )
            return [{}]
        # Query geocoder to find the best location in photon for that particular query
        initial_results = self._get_geocode_info(location, best_matching, country)
        # Validate result with geonames service
        validated_results = []
        for geocode_hit in initial_results:
            # Validate with geonames
            validated_hits = self._get_geonames_info(
                geocode_hit["name"], geocode_hit["country"]
            )
            for validated_hit in validated_hits:
                # where the geonames validation magic happens
                if validated_hit["name"].lower() == geocode_hit["name"].lower():
                    if (
                        validated_hit["country"].lower()
                        == geocode_hit["country"].lower()
                    ):
                        validated_results.append(geocode_hit)
                else:
                    continue
        if validated_results == []:
            validated_results = [{}]
            logging.warning(
                f"Location validation failed for {location}. Returning empty result"
            )

        return validated_results

    def get_country_neighbors(self, country: str) -> List[str]:
        """
        This function returns the countries that have a common
        border with the country specified in input.

        :param country: string of the country name to look for its
                        neighbors.
        """

        return self.map_country_neighbors[country]

    def reverse_geocode_bounding_box(self, bounding_box: List[float]) -> List[str]:

        countries_in_bbox = []

        for country in self.country_bbox.keys():
            if self.check_intersection(bounding_box, self.country_bbox[country]):
                countries_in_bbox.append(country)

        return countries_in_bbox

    def filter_ner_countries(
        self, ner_tags: List[Dict[str, any]]
    ) -> List[Dict[str, any]]:
        """
        This function gathers all ner locations tags and filters them to select
        locations being countries.
        It makes use of the countries_bbox to filter out countries and
        returns a list of the countries and local locations found in the text.

        :params ner_tags:           List of dictionaries containing NER tags

        :returns ner_country_tags:  List of dictionaries containing NER country tags
        :returns ner_local_location_tags:  List of dictionaries containing NER local location tags
        """

        ner_country_tags = []
        ner_local_tags = []
        for tag in ner_tags:
            if tag["label"] == "location":
                if tag["name"].lower() in self.country_bbox.keys():
                    ner_country_tags.append(tag)
                else:
                    ner_local_tags.append(tag)
        return ner_country_tags, ner_local_tags

    def update_mapping_countries(
        self,
        mapping_countries: Dict[str, any],
        name: str,
        old_country: str,
        new_country: str,
    ):
        """
        This functions aims to update the mapping of countries
        by using the majority votes available.

        :params mapping_countries:          Dictionary of locations to be updated
        :params name:                       String of Local Location to be updated
        :params old_country:                String of Country to be updated
        :params new_country:                String containing country to be used
                                            to update mappings_country dictionary

        :returns mapping_countries:         Updated Dictionary of mappings of countries
                                            used to update locations
        """
        if old_country != new_country:
            new_location = self.get_location_info(
                name, country=new_country, best_matching=True
            )
            # check if the reference country can be used for this location
            if new_location != [{}]:
                mapping_countries[name] = new_location[0]["country"]

        return mapping_countries

    def double_check_countries(
        self,
        locations: List[Dict[str, any]],
        ner_tags: List[Dict[str, any]],
        top_countries: int = None,
    ) -> List[Dict[str, any]]:
        """
        This function tries to detect a reference set of countries from
        a list of locations, assigning misrepresented locations to them.
        In other words, if the locations are four cities in Texas, Houston,
        Sacramento, San Antonio and Paris, we want to avoid that the first
        three are assigned to the United States and the latter to France.
        To do this we try to assign every location to the most frequent
        countries in the list, if possible. The parameter top_countries
        specifies how many countries to check, default is None that is
        every country found in the locations list is checked as reference
        state if appears more than once in the list.
        The function returns a new list of locations with new inferred countries
        if possible.

        :param locations:           list of dictionaries that represents a location
                                    as produced by the get_location_info method
        :param top_countries:       integer that put a maximum bound on the
                                    number of countries to check as a reference
        :param ner_location_tags:   list of ner tags associated to locations to
                                    be filtered to countries
        """
        # Get ner countries and init ner_countries_count list
        ner_countries, ner_local = self.filter_ner_countries(ner_tags)
        ner_countries_count = []

        # Extract uk nations
        ner_uk_nations = [
            tag["name"]
            for tag in ner_local
            if tag["name"].lower()
            in ["england", "wales", "northern ireland", "scotland"]
        ]
        # Normalise country name
        if ner_countries:
            ner_countries = [
                self.get_location_info(
                    tag["name"], country=tag["name"], best_matching=True
                )[0]
                for tag in ner_countries
            ]
            # Create ner countries list
            for ner_country in ner_countries:
                if ner_country:
                    ner_countries_count.append(ner_country["country"])

        # create a default mapping and extract all the countries
        countries, only_countries, mapping_countries = self.extract_countries(locations)
        # extract the candidate reference countries
        majority = self.count_countries(countries, top_countries)
        ner_majority = self.count_countries(ner_countries_count, top_countries)

        # If there's only one country in the majority
        if len(majority) <= 1 or majority[0][1] == 1:
            logging.info(
                "Location Edge Case 0 detected: Only one country detected in event locations"
            )
            if not locations[0] or not "name" in locations[0]:
                logging.warning(
                    "Location Edge Case 0.1 detected: Local location empty - returning empty location"
                )
                return [{}]

        ## Edge case 1: If there are few locations and 1 is a country
        ## We assume that the few locations belong to that country,
        ## so that country is the new country location
        if len(only_countries) == 1:
            logging.info(
                "Location edge case 1 detected: There are few event locations and one is a country - {only_countries}"
            )
            new_country = list(only_countries.keys())[0]
            for name, country in mapping_countries.items():
                mapping_countries = self.update_mapping_countries(
                    mapping_countries, name, country, new_country
                )

        ## Edge case 2: If there are references to multiple countries including or not local locations
        ## We assume no majority can be reached and local locations will be included
        ## if they match with one of the countries, others will be discarded
        elif len(only_countries) > 1:
            logging.warning(
                f"Location edge case 2 Detected: Found {len(only_countries)} references to countries, locations not matching one of those countries will be discarded"
            )
        ## Edge case 5: UK/US/CA location issue when nothing else works
        elif ner_uk_nations != []:
            logging.warning(
                "Location edge case 5 case detected: UK nations found in text, assigning local locations to UK if they exist in the UK"
            )
            new_country = "United Kingdom"
            for name, country in mapping_countries.items():
                # the location is a country no need to check it
                if name == country:
                    continue
                mapping_countries = self.update_mapping_countries(
                    mapping_countries, name, country, new_country
                )
        ## Edge case 4: There's a tie between countries
        elif len(majority) > 1 and majority[0][1] == majority[1][1]:
            logging.info(
                "Location edge case 4 case Detected: There's a tie between majority countries"
            )
            # If majority cannot be reached, then look at ner tags for majority countries
            if ner_majority:
                if ner_majority[0][1] >= 1:
                    for name, country in mapping_countries.items():
                        # the location is a country no need to check it
                        if name == country:
                            continue
                        # iterating from the most frequent country
                        for reference_country in ner_majority:
                            if reference_country[1] == 1 and len(ner_majority) > 1:
                                break
                            mapping_countries = self.update_mapping_countries(
                                mapping_countries, name, country, reference_country[0]
                            )
            else:
                logging.warning(
                    f"No country ner tags found. Majority couldn't be stablished. ner_majority: {ner_majority}"
                )
        ## Edge case 3: Multiple locations with a clear majority
        else:
            logging.info(
                "Location edge case 3 case Detected: Assigning majority country to all local locations"
            )
            for name, country in mapping_countries.items():
                # the location is a country no need to check it
                if name == country:
                    continue
                # iterating from the most frequent country
                for reference_country in majority:
                    if reference_country[1] == 1:
                        break
                    mapping_countries = self.update_mapping_countries(
                        mapping_countries, name, country, reference_country[0]
                    )
        # Update new locations
        new_locations = self.update_country_for_locations(
            locations, mapping_countries, only_countries
        )

        return new_locations

    def update_country_for_locations(
        self,
        locations: List[Dict[str, Any]],
        mapping_countries: Dict[str, int],
        only_countries: Dict,
    ) -> List[Dict[str, Any]]:
        """
        This functions takes a list of locations and updates the country of each location
        based on the mapping countries dictionary and the only_countries dictionary

        :params locations:          List of locations to be updated
        :params mapping_countries:  Dict containing mappings between local locations and countries
        :params only_countries:     Dict containing only country locations

        :return new_locations:      List of new locations after update has been completed
        """
        new_locations = []

        for location in locations:
            if not location or not "name" in location:
                new_locations.append({})
                continue
            if location == []:
                new_locations.append({})
                continue
            if location["name"] not in mapping_countries:
                new_locations.append({})
                continue
            new_country = mapping_countries[location["name"]]
            new_location = None
            # check that countries are different in order to update location
            if new_country != location["country"]:
                logging.info(f'Changing {location["country"]} to {new_country}')
                new_location = self.get_location_info(
                    location["name"],
                    country=new_country,
                    best_matching=True,
                )
            # Check that new location exists and requirements are fullfilled
            new_locations.append(
                self.check_new_location(new_location, location, only_countries)
            )
        return new_locations

    def check_new_location(
        self, new_location: Dict, location: Dict, only_countries: Dict
    ) -> Dict:
        """
        This function checks that a new location can be added to
        the new location list. It returns the desired output
        based on certain parameters

        :params new_location:       Dictionary containing new location
        :params location:           Dictionary containing old location
        :params only_countries:     Dictionary containing only country locations

        :return :
        """
        if new_location:
            return new_location[0]
        if location["country"] in only_countries:
            return location
        if not only_countries:
            return location
        return {}

    def extract_countries(self, locations: List[Dict]) -> Tuple[List, Dict, Dict]:
        """
        This function takes a list of locations and populates the countries list,
        the only_countries dictionary and the mapping_countries dictionary
        with country and local information.
        :params locations:          List of locations to be extracted

        :returns countries:         List of countries found in locations
        :returns only_countries:    Dictionary containing count of country mentions
        :returns mapping_countries: Dictionary containing mappings between locations and their countries
        """
        mapping_countries = {}
        only_countries = {}
        countries = []
        for location in locations:
            if not location or not "name" in location:
                continue
            if not isinstance(location, list):
                if "country" not in location or location["country"] == []:
                    continue
                countries.append(location["country"])
                mapping_countries[location["name"]] = location["country"]
                if location["name"] == location["country"]:
                    # Check how many mentions to countries there are
                    if location["country"] in only_countries:
                        only_countries[location["country"]] += 1
                    else:
                        only_countries[location["country"]] = 1
            else:
                for l in location:
                    if l["country"] == []:
                        continue
                    countries.append(l["country"])
                    mapping_countries[l["name"]] = l["country"]
                    if l["name"] == l["country"]:
                        if l["country"] in only_countries:
                            only_countries[l["country"]] += 1
                        else:
                            only_countries[l["country"]] = 1
        return countries, only_countries, mapping_countries

    def count_countries(
        self, countries: List[str], top_countries: int = None
    ) -> List[Tuple[str, int]]:
        """
        This function takes a list of countries and computes a count of terms
        with the option of only country the most common ones

        :params countries:      List of countries to be counted
        :params top_countries:  Int defining how many most common countries to count

        :returns majority:      List of tuples containing the count of countries
        """
        if not top_countries:
            majority = Counter(countries).most_common()
        else:
            majority = Counter(countries).most_common(top_countries)
        return majority

    def get_distance(self, *params):
        """
        This function is a wrapper of the calculate_distance
        function from utils.

        :params param: two lists of coordinates and and an
                       optional string that represents the
                       distance function to use.
        """

        return calculate_distance(*params)

    def bounding_box_to_point(self, *params):
        """
        This function is a wrapper of the calculate_distance
        function from utils.

        :params param: a list of four floats representing the
                       bounding box to transform and an
                       optional string that represents the
                       transform function to use.
        """

        return bbox2point_coord(*params)

    def enlarge_bounding_box(
        self, coordinates: List[float], distance: float
    ) -> List[float]:
        """
        This function checks if a bounding box has a diagonal that is larger
        than or equal to the distance passed in input. If it is not, the bounding
        box is enlarged until it reaches the required distance and returned.

        :param coordinates: list of floats representing the two sets of
                            coordinates that define a bounding box
        :param distance:    a float giving the required distance between
                            the corners of the considered bounding box
        """

        diagonal = self.get_distance(coordinates[:2], coordinates[2:])
        if diagonal > distance:
            return coordinates

        return edit_bounding_box(coordinates, distance - diagonal, add=True)

    def check_intersection(
        self, bounding_box_1: List[float], bounding_box_2: List[float]
    ) -> bool:
        """
        This function takes in input two bounding boxes, represented by
        two sets of coordinates, and checks if these two boxes have a not null
        intersection, returning True if it is so, False otherwise.

        :param bounding_box_1: list of floats representing the two sets of
                               coordinates that define a bounding box
        :param boundinb_box_2: list of floats representing the two sets of
                               coordinates that define a bounding box
        """

        # this is not ideal at the poles, but it is good for now
        # who cares about penguins by the way?

        if bounding_box_1 == bounding_box_2:
            return True

        bounding_box_1 = gps_sanity_check(bounding_box_1)
        bounding_box_2 = gps_sanity_check(bounding_box_2)

        dist1 = self.get_distance(bounding_box_1[:2], bounding_box_1[2:])
        dist2 = self.get_distance(bounding_box_2[:2], bounding_box_2[2:])

        # this is because if one bbox is contained in another
        # this function is not symmetric anymore
        if dist2 > dist1:
            bounding_box_2, bounding_box_1 = bounding_box_1, bounding_box_2

        minlon1, minlat1, maxlon1, maxlat1 = bounding_box_1
        minlon2, minlat2, maxlon2, maxlat2 = bounding_box_2

        minlat1 = _wrap_latitude(minlat1)
        minlat2 = _wrap_latitude(minlat2)
        maxlat1 = _wrap_latitude(maxlat1)
        maxlat2 = _wrap_latitude(maxlat2)

        rabx = abs(minlon1 + maxlon1 - minlon2 - maxlon2)
        raby = abs(minlat1 - minlat2 + maxlat1 - minlat2)

        rx = maxlon1 - minlon1 + maxlon2 - minlon2
        ry = minlat1 - maxlat1 + minlat2 - maxlat2

        if rabx <= rx and raby <= ry:
            return True

        return False

    def merge_bounding_boxes(self, bounding_boxes: List[List[float]]) -> List[float]:
        """
        This function takes in input a list of bounding boxes and merges them
        producing their union, the minimal bounding box that contains all the
        others.

        :param bounding_boxes: list of bounding boxes, each of them a list
                               of four float (min_lon,min_lat,max_lon,max_lat)
        """

        min_lon = min([b[0] for b in bounding_boxes])
        min_lat = max([b[1] for b in bounding_boxes])
        max_lon = max([b[2] for b in bounding_boxes])
        max_lat = min([b[3] for b in bounding_boxes])

        return gps_sanity_check([min_lon, min_lat, max_lon, max_lat])

    def check_large_bounding_box(
        self, bounding_box: List[float], threshold: float = 175
    ) -> List[float]:
        """
        This function takes in input a list of bounding boxes and merges them
        producing their union, the minimal bounding box that contains all the
        others.

        :param bounding_box:   bounding boxes, list of four
                               float (x1,y1,x2,y2)
        :param threshold:      Float refering to the limit
                               in which a bounding box is considered too large
        """
        threshold = abs(threshold)

        x1, y1, x2, y2 = bounding_box

        # Make sure that no pair of coordinates goes under -175 and over 175 in both ends.
        # Sometimes the coordinates come flipped so we'll check each pair.
        # I have chosen 175 to be the threshold because in 175 you can find the end of new zealand
        # and at -175 the end of alaska
        if ((x1 <= -threshold) and (x2 >= threshold)) or (
            (x2 <= -threshold) and (x1 >= threshold)
        ):
            return True
        if ((y1 <= -threshold) and (y2 >= threshold)) or (
            (y2 <= -threshold) and (y1 >= threshold)
        ):
            return True
        return False
