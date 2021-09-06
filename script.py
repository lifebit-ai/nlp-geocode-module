import argparse
import json
import os
import logging
from geocoder import Geocoder
from utils import str2bool


logging.basicConfig(
    level=logging.DEBUG,
    format="%(asctime)s.%(msecs)03d %(levelname)s: %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)

if __name__ == "__main__":

    parser = argparse.ArgumentParser(
        description="""This script extracts location coordinates for
                    events extracted from the nlp pipeline. """
    )

    parser.add_argument(
        "-d",
        "--data",
        help="file or folder where to read the list of events",
        type=str,
        required=True,
        dest="data_path",
    )

    parser.add_argument(
        "-c",
        "--config",
        help="config file for the geocoder",
        type=str,
        required=False,
        default="config.yaml",
        dest="config_path",
    )

    parser.add_argument(
        "-k",
        "--double_check",
        type=str2bool,
        help="""If True the script will try to infer the reference country from  all the locations and assign""",
        required=False,
        default=True,
        dest="double_check",
    )

    parser.add_argument(
        "-o",
        "--output",
        type=str,
        help="""Name of output file""",
        required=False,
        default="output.json",
        dest="output_path",
    )

    parser.add_argument(
        "-s",
        "--strict",
        type=str2bool,
        help="""If True failed query for the location will delete the event""",
        required=False,
        dest="strict",
    )

    args = parser.parse_args()
    logging.info(args)

    # create geocoder
    geocoder = Geocoder(args.config_path)

    # read data
    if os.path.isdir(args.data_path):
        data = [
            json.load(open(d, "r")) for d in os.listidir(args.data_path) if ".json" in d
        ]
    else:
        data = json.load(open(args.data_path, "r"))

    if not isinstance(data, list):
        data = [data]

    data_with_coordinates = []

    # this map will store found location avoiding a new call for already seen locations
    location_map = {}

    for d in data:
        if not "events" in d.keys():
            continue
        if d["events"] == []:
            continue
        for event in d["events"]:
            if event["location"] in location_map.keys():
                coordinates = location_map[event["location"]]
            else:
                # location not seen before call the geocoder
                coordinates = geocoder.get_coordinates(event["location"])
                location_map[event["location"]] = coordinates
            # store the coordinates in the new field of the event item
            event["coordinates"] = coordinates

        if args.strict:
            # here we remove events where no coordinates were found for its location
            correct_events = []
            for event in d["events"]:
                if event["coordinates"] != []:
                    correct_events.append(event)
            d["events"] = correct_events

        if args.double_check:
            # here we double check if we are assigning the correct country based
            # on the textual context
            sample_coordinates = [event["coordinates"] for event in d["events"]]

            # get the mapping with the new reference countries in place
            mapping_countries = geocoder.double_check_countries(sample_coordinates)

            # update the events with the correct country for each set of coordinates
            for event in d["events"]:
                if "coordinates" in event.keys():
                    new_coordinates = []
                    for coords in event["coordinates"]:
                        new_country = mapping_countries[coords["name"]]
                        new_coords = None
                        if new_country != coords["country"]:
                            new_coords = geocoder.get_coordinates(
                                coords["name"],
                                country=new_country,
                                best_matching=True,
                            )
                        if new_coords:
                            new_coordinates.append(new_coords)
                        else:
                            new_coordinates.append(coords)
                    event["coordinates"] = new_coordinates

        data_with_coordinates.append(d)
        break

    json.dump(data_with_coordinates, open(args.output_path, "w"))
