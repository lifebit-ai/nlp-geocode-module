from geocoder_module.helpers import check_location_can_be_processed


class TestCheckFormat:
    def test_no_symbols_and_digits_in_location(self):
        location = "U.S."
        response = check_location_can_be_processed(location)
        assert response == True
        location = "Alabama"
        response = check_location_can_be_processed(location)
        assert response == True

    def test_symbols_in_location(self):
        location = "(U.S.) "
        response = check_location_can_be_processed(location)
        assert response == False

    def test_digits_in_location(self):
        location = "H5N8"
        response = check_location_can_be_processed(location)
        assert response == False

    def test_real_examples_symbols_and_digits(self):
        location = "Southern Ontario (IP2)"
        response = check_location_can_be_processed(location)
        assert response == False
        location = "Fukushima-city2"
        response = check_location_can_be_processed(location)
        assert response == False
