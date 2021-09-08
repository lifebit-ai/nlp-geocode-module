### Geocoder module

This repository contains the code for the Geocoder module, that provides coordinates from the normalised name of a location, alongside with its country and the bounding box coordinates of its area (top left corner and bottom right corner). This class is an interface to the `Photon` geocoder; its entrypoint has to be provided in the config file used as input for the module (default `config.yaml`).

The parameters for the config file are:
 * `url_api`: api endpoint for the `Photon` geocoder, e.g.  "http://32.101.121.10:2332/api?"
 * `url_reverse`: api endpoint for the `Photon` decoder (to get location from coordinates, not implemented for future use), e.g  "http://32.101.121.10:2332/reverse?"
 * `lang`: parameter to specify the language of the returned results, default is `"en"` 
 * `osm_keys`: list of filters on the geocoder results, based on Open Stree Map features https://wiki.openstreetmap.org/wiki/Map_features. Default is `place` 


To usage of the `script.py` file is the following

```
usage: script.py [-h] -d DATA_PATH [-c CONFIG_PATH] [-k DOUBLE_CHECK] [-o OUTPUT_PATH]
                 [-s STRICT]
script.py: error: the following arguments are required: -d/--data

```

where `DATA_PATH` is the path of a `JSON` file or a folder containign `JSON` files. Every stored dictionary has to have a field `events` which contains a subfield `location`. `CONFIG_PATH` specifies the path where the  configuration file for the geocoder is stored, by default is `config.yaml`. The `DOUBLE_CHECK` parameter is a bool value, if True the model tries  to detect a reference set of countries from a list of locations, assigning misrepresented locations to them.
In other words, if the locations are four cities in Texas, Houston, Sacramento, San Antonio and Paris, we want to avoid that the first three are assigned to the United States and the latter to France. To do this we try to assign every location to the most frequent countries in the list, if possible. `STRICT` is another bool parameter,if True the script will remove events where the query for the location has returned no results. Finally, `OUTPUT_PATH` is the path of the `JSON` file where to store the final results.
