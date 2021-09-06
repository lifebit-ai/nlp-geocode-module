### Geocoder module

This repository contains the code for the Geocoder module, that provides coordinates from the normalised name of a location, alongside with its country and the bounding box coordinates of its area (top left corner and bottom right corner). This class is an interface to the `Photon` geocoder; its entrypoint has to be provided in the config file used as input for the module (default `config.yaml`).

The parameters for the config file are:
 * `url_api`: api endpoint for the `Photon` geocoder, e.g.  "http://32.101.121.10:2332/api?"
 * `url_reverse`: api endpoint for the `Photon` decoder (to get location from coordinates, not implemented for future use), e.g  "http://32.101.121.10:2332/reverse?"
 * `lang`: parameter to specify the language of the returned results, default is `"en"` 
 * `osm_keys`: list of filters on the geocoder results, based on Open Stree Map features https://wiki.openstreetmap.org/wiki/Map_features. Default is `place` 
