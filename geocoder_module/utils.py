import math
import logging
from itertools import product
from typing import List, Union

logging.basicConfig(
    level=logging.DEBUG,
    format="%(asctime)s.%(msecs)03d %(levelname)s: %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)

EARTH_RADIUS = 6371e3
ALLOWED_DISTANCES = ["harvesin"]


def str2bool(v: Union[str, bool]) -> bool:
    """
    This function check if the passed argument is boolean
    or it translates to the correct bool if v is a valid string
    """
    if isinstance(v, bool):
        return v
    if v.lower() in ("yes", "true", "t", "y", "1"):
        return True
    elif v.lower() in ("no", "false", "f", "n", "0"):
        return False
    else:
        raise argparse.ArgumentTypeError("Boolean value expected.")


def harvesin(
    latitude_a: float, longitude_a: float, latitude_b: float, longitude_b: float
) -> float:
    """
    This is the implementation of the harvesin function to get the distance
    (in meters) between two sets of coordinates.

    :param latitude_a: float that represents the latitude of the first coordinate
    :param latitude_a: float that represents the longitude of the first coordinate
    :param latitude_b: float that represents the latitude of the second coordinate
    :param latitude_a: float that represents the longitude of the second coordinate
    """

    ph1 = latitude_a * math.pi / 180
    ph2 = latitude_b * math.pi / 180
    delta_phi = (latitude_b - latitude_a) * math.pi / 180
    delta_gamma = (longitude_b - longitude_a) * math.pi / 180

    a = math.sin(delta_phi / 2) * math.sin(delta_phi / 2) + math.cos(ph1) * math.cos(
        ph2
    ) * math.sin(delta_gamma / 2) * math.sin(delta_gamma / 2)
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))

    return EARTH_RADIUS * c


def calculate_distance(
    coordinates_1: List[float], coordinates_2: List[float], function: str = "harvesin"
) -> float:
    """
    This function measures the distance between two sets of coordinates using the
    distance function passed as inputs. The distance can be measured between two
    points coordinates (two lists composed of longitude and latidue in float values),
    or two bounding boxes (two lists composed of two couples of longitude
    and latitude each); in the latter case the minimum distance between the
    two bounding boxes is returned. The returned distance is measured in meters.

    :param coordinates_1: list composed of two or four floats
    :param coordinates_2: list composed of two or four floats
    :param function:      string that represents the function distance to use
    """

    if not function in ALLOWED_DISTANCES:
        logging.warning("{} is not implemented yet".format(function))
        raise NotImplementedError

    # TODO: extend to distance between bounding boxes and single point coordinates
    if len(coordinates_1) != len(coordinates_2):
        logging.error(
            "The two sets of coordinates have different lenghts {} and {}".format(
                len(coordinates_1), len(coordinates_2)
            )
        )
        return None

    if len(coordinates_1) == 2:
        lon_1, lat_1 = coordinates_1
        lon_2, lat_2 = coordinates_2

        return eval(function)(lat_1, lon_1, lat_2, lon_2)

    if len(coordinates_1) == 4:
        a = coordinates_1[:2]
        b = coordinates_1[2:]
        c = coordinates_2[:2]
        d = coordinates_2[2:]

        corners = product([a, b], [c, d])
        min_distance = 2 * math.pi * EARTH_RADIUS

        for corner in corners:
            distance = eval(function)(
                corner[0][1], corner[0][0], corner[1][1], corner[1][0]
            )
            if distance < min_distance:
                min_distance = distance

        return min_distance

    logging.error(
        """The set of coordinates are composed of two pairs of coordinates, or two
         sets of four coordinates. Here we have {} elements""".len(
            coordinates_1
        )
    )
    return None
