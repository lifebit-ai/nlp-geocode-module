import re


def check_location_can_be_processed(location: str) -> bool:
    """Checks if a location can be processed by the geocoder system by
    checking a regexes containing forbidden special characteres and digits
    :params location:       String containing location to be checked"""
    # This pattern will detect any of the symbols -!@#$%&*<>?_{}[]()
    # involved as well as any digit between 0 and 9
    regex_pattern = re.compile(r"[-!@#$%&*<>?_\{\}\[\]\(\)]|[0-9]")
    if regex_pattern.findall(location):
        return True
    return False
