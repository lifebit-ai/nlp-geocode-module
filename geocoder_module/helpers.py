import re
import json
import os
import sys
from logger.logging import logging
import geocoder_module


def check_location_can_be_processed(location: str) -> bool:
    """Checks if a location can be processed by the geocoder system by
    checking a regexes containing forbidden special characteres and digits
    :params location:       String containing location to be checked"""
    # This pattern will detect any of the symbols -!@#$%&*<>?_{}[]()
    # involved as well as any digit between 0 and 9
    regex_pattern = re.compile(r"[-!@#$%&*<>?_\{\}\[\]\(\)]|[0-9]")
    if regex_pattern.findall(location):
        return False
    return True


def load_json_file(file_name: str):
    """
    Loads json file in geocoder module folder
    :params file_name:      String containing filename to be loaded from geocoder_module folder
    """
    try:
        file_path = os.path.join(
            os.path.dirname(os.path.dirname(geocoder_module.__file__)),
            "geocoder_module",
            file_name,
        )
        with open(file_path, "r", encoding="utf-8") as f:
            data = json.load(f)
            return data
    except Exception as error:
        logging.error(
            f"{error} The json file {file_name} specified in the configuration can't be read."
        )


def check_env_vars():
    """
    Checks that env variables are being loaded succesfully
    """
    try:
        logging.debug("Using Photon Geocoder server on: " + os.environ["PHOTON_SERVER"])
    except Exception as error:
        logging.error(
            f"{error} - The environment variable PHOTON_SERVER has not been specified"
        )
        sys.exit(-1)

    try:
        logging.debug("Using Geonames server on: " + os.environ["GEONAMES_SERVER"])
    except Exception as error:
        logging.error(
            f"{error} - The environment variable GEONAMES_SERVER has not been specified"
        )
        sys.exit(-1)
