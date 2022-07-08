import sys
import json
from geocoder_module.geocoder import Geocoder

geocoder = Geocoder()

if __name__ == "__main__":
    in_file = sys.argv[1]
    locations = json.load(open(in_file, "r"))[0]
    results = []
    for key in locations.keys():
        output_dict = {}
        location = locations[key]
        try:
            print(f"Querying location: {location}")
            predicted_location_validation = geocoder.get_location_from_coordinates(
                location["latitude"],
                location["longitude"],
                location["localLocation"],
                location["country"],
                True,
                0.1,
                False,
            )
        except:
            predicted_location = {}
        output_dict["real"] = location
        output_dict["predicted"] = predicted_location
        results.append(output_dict)
    with open(f"results_location_data.json", "w", encoding="utf-8") as f:
        json.dump(results, f, ensure_ascii=False, indent=4)
