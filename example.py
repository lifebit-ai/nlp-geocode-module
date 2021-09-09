from geocoder_module.geocoder import Geocoder

geocoder_module = Geocoder("geocoder_module/config.yaml")
location_info = geocoder_module.get_location_info("saratoga")

double_checked_location_info = geocoder_module.double_check_countries(location_info)

print("coordinates: ", location_info)
print("")
print("map_of_countries: ", double_checked_location_info)
