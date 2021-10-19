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
ALLOWED_TRANSFORMS = ["average"]


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


def average(bounding_box: List[float]):
    """
    This function returns the simple mean average
    of the coordinates that describes a bounding box
    (lon_min,lat_min,lon_max,lat_max)

    :param bounding_box: list of four floats describing
                         lon_min,lat_min,lon_max,lat_max
    """

    lon_min, lat_min, lon_max, lat_max = bounding_box

    lon = (lon_min + lon_max) / 2
    lat = (lat_min + lat_max) / 2

    return [lon, lat]


def bbox2point_coord(
    bounding_box: List[float], function_name: str = "average"
) -> List[float]:
    """
    This function transforms a bounding box in a single point
    coordinates using the function specified as input (default is the
    average function)

    :param boundinb_box:  a list of 4 floats lon_min,lat_min,lon_max,lat_max
    :param function_name: a string representing the function used to transform
                          the bounding box to a point coordinate

    """
    if not function_name in ALLOWED_TRANSFORMS:
        logging.warning("{} is not implemented yet".format(function_name))
        raise NotImplementedError

    point_coord = eval(function_name)(bounding_box)

    return point_coord


def calculate_distance(
    coordinates_1: List[float],
    coordinates_2: List[float],
    function_name: str = "harvesin",
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
    :param function_name:      string that represents the function distance to use
    """

    if not function_name in ALLOWED_DISTANCES:
        logging.warning("{} is not implemented yet".format(function_name))
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

        return eval(function_name)(lat_1, lon_1, lat_2, lon_2)

    if len(coordinates_1) == 4:
        a = coordinates_1[:2]
        b = coordinates_1[2:]
        c = coordinates_2[:2]
        d = coordinates_2[2:]

        corners = product([a, b], [c, d])
        min_distance = 2 * math.pi * EARTH_RADIUS

        for corner in corners:
            distance = eval(function_name)(
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


def edit_bounding_box(
    coordinates: List[float],
    distance_to_add: float,
    add: bool = True,
) -> List[float]:
    """
    This function takes in input a list of coordinates representing a bounding
    box, that is two sets of gps coordinates (longitude,latitudes) and increase
    or decrease its diagonal by the distance passed in input returning
    the new sets of coordinates.

    :param coordinates:       list of floats representing the two sets of
                              coordinates that define a bounding box
    :param distance_to_reach: a float value that is the distance added or
                              the diagonal of the bounding box should have
    :param add:               bool value if True the distance is added
                              otherwise is subtracted

    """

    dist = distance_to_add / 2
    dist = -dist if not add else dist

    m = 1 / ((2 * math.pi / 360) * EARTH_RADIUS)

    lon_1, lat_1, lon_2, lat_2 = coordinates

    new_lat_1 = lat_1 + dist * m
    new_lat_2 = lat_2 - dist * m

    new_lon_1 = lon_1 - (dist * m) / math.cos(lat_1 * (math.pi / 180))
    new_lon_2 = lon_2 + (dist * m) / math.cos(lat_2 * (math.pi / 180))

    new_coords = gps_sanity_check([new_lon_1, new_lat_1, new_lon_2, new_lat_2])

    return new_coords


def gps_sanity_check(bounding_box: List[float]) -> List[float]:
    """
    This function ensures that a bounding box is represented
    by two sets of coordinates, the first one is the top left
    corner and the remainig two the coordinates of the bottom
    right corner of the bounding box (min lon, min lat, max lon,
    max lat).
    If this is not true it tries to fix it and return a correct
    bounding box.

    :param bounding_box: list of floats representing the coordinates
                         of the bounding box
    """

    if len(bounding_box) != 4:
        logging.error(
            """The input bounding box has {} coordinates
                       which is wrong! They need to be 4!""".format(
                len(coordinates)
            )
        )
        return None

    # left!
    if not bounding_box[0] < bounding_box[2]:
        logging.warning(
            "{} is not in the right format, changed it!".format(bounding_box)
        )
        bounding_box[2], bounding_box[0] = bounding_box[0], bounding_box[2]

    # right!
    if not bounding_box[1] > bounding_box[3]:
        logging.warning(
            "{} is not in the right format, changed it!".format(bounding_box)
        )
        bounding_box[3], bounding_box[1] = bounding_box[1], bounding_box[3]

    return bounding_box
