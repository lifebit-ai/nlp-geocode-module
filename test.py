from geocoder_module.geocoder import Geocoder

geocoder_module = Geocoder("geocoder_module/config.yaml")
coordinates = geocoder_module.get_location_info("saratoga")

map_of_countries = geocoder_module.double_check_countries(coordinates)

print("coordinates", coordinates)
# print("")
print("map_of_countries", map_of_countries)
