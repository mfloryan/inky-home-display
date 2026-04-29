from icons import load_icon


class TestLoadIcon:
    def test_returns_rgb_image_for_known_ow_code(self):
        img = load_icon("01d", 32)
        assert img.mode == "RGB"

    def test_32px_icon_has_correct_dimensions(self):
        img = load_icon("01d", 32)
        assert img.size == (32, 32)

    def test_16px_icon_has_correct_dimensions(self):
        img = load_icon("01d", 16)
        assert img.size == (16, 16)

    def test_icon_background_is_white(self):
        img = load_icon("01d", 32)
        assert img.getpixel((0, 0)) == (255, 255, 255)

    def test_night_code_loads_moon_icon(self):
        img = load_icon("01n", 32)
        assert img.size == (32, 32)

    def test_snow_icon_loads_for_16px(self):
        img = load_icon("13d", 16)
        assert img.size == (16, 16)

    def test_all_ow_codes_load_without_error(self):
        codes = [
            "01d", "01n", "02d", "02n", "03d", "03n", "04d", "04n",
            "09d", "09n", "10d", "10n", "11d", "11n", "13d", "13n",
            "50d", "50n",
        ]
        for code in codes:
            for size in (16, 32):
                img = load_icon(code, size)
                assert img.size == (size, size), f"Wrong size for {code} at {size}px"
