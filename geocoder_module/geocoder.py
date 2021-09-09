import requests
import yaml
import logging
import sys
import math
from collections import Counter
from itertools import product
from typing import Dict, List
from geocoder_module.utils import calculate_distance

logging.basicConfig(
    level=logging.DEBUG,
    format="%(asctime)s.%(msecs)03d %(levelname)s: %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)


class Geocoder:
    def __init__(self, config: str = "") -> None:
        """
        This class creates the Geocoder module, that is an object
        to get coordinates from the normalised name of a location,
        alongside with its country and the bounding box coordinates
        of its area (top left corner and bottom right corner).
        The object is an interface to the Photon geocoder; its entrypoint
        has to be provided in the config file.

        :param config: string path for the config file
        """

        try:
            self.config = yaml.load(open(config, "r"), Loader=yaml.FullLoader)
        except FileNotFoundError:
            logging.error("The config file {} doesn't exist".format(config))
            sys.exit(-1)
        except:
            logging.error("Error reading config file {}".format(config))
            sys.exit(-1)

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

        try:
            response = requests.get(
                self.config["url_api"],
                params={
                    "q": location,
                    "lang": self.config["lang"],
                    "osm_tag": self.config["osm_keys"],
                },
            )
            response = response.json()
        except Exception as e:
            logging.error("Error in querying location {} ".format(location))
            logging.error(e)

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

            location["name"] = features["properties"]["name"]
            location["bounding_box"] = features["properties"]["extent"]
            location["country"] = features["properties"]["country"]
            location["coordinates"] = features["geometry"]["coordinates"]
            results.append(location)

            # the first results is the always the best matching one
            if best_matching:
                break

        return results

    def double_check_countries(
        self, locations: List[Dict[str, any]], top_countries: int = None
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

        :param locations:      list of dictionaries that represents a location
                               as produced by the get_coordinates method
        :param top_countries:  integer that put a maximum bound on the
                               number of countries to check as a reference
        """

        mapping_countries = {}

        countries = []

        # create a default mapping and extract all the countries
        for location in locations:
            if not isinstance(location, list):
                if location["country"] == []:
                    continue
                countries.append(location["country"])
                mapping_countries[location["name"]] = location["country"]
            else:
                for l in location:
                    if l["country"] == []:
                        continue
                    countries.append(l["country"])
                    mapping_countries[l["name"]] = l["country"]

        # extract the candidate reference countries
        if not top_countries:
            majority = Counter(countries).most_common()
        else:
            majority = Counter(countries).most_common(top_countries)

        if len(majority) <= 1 or majority[0][1] == 1:
            logging.warning(
                """All the locations belong to the same country or no
                   reference country can be inferred from the text"""
            )
            return locations

        for name, country in mapping_countries.items():
            # the location is a country no need to check it
            if name == country:
                continue
            # iterating from the most frequent country
            for reference_country in majority:
                if reference_country[1] == 1:
                    break
                reference_country = reference_country[0]
                if country != reference_country:
                    new_location = self.get_coordinates(
                        name, country=reference_country, best_matching=True
                    )

                    # check if the refernce country can be used for this location
                    if new_location != []:
                        mapping_countries[name] = new_location[0]["country"]
                        break
                else:
                    break

        new_locations = []

        for location in locations:
            if location == []:
                new_locations.append([])
                continue
            new_country = mapping_countries[location["name"]]
            new_location = None
            if new_country != location["country"]:
                new_location = self.get_location_info(
                    location["name"],
                    country=new_country,
                    best_matching=True,
                )
            if new_location:
                new_locations.append(new_location)
            else:
                new_locations.append(location)

        return new_locations

    def get_distance(self, *params):
        """
        This function is a wrapper of the calculate_distance
        function from utils.

        :params param: two lists of coordinates and and an
                       optional string that represents the
                       distance function to use.
        """

        return calculate_distance(*params)
