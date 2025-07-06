from PIL import ImageFont


class FontLoader:
    def __init__(self):
        self._cache = {}

    def _cached_font(self, cache_key, loader_func):
        if cache_key not in self._cache:
            self._cache[cache_key] = loader_func()
        return self._cache[cache_key]

    def ubuntu_regular(self, size):
        return self._cached_font(
            f"ubuntu_regular_{size}",
            lambda: ImageFont.truetype(
                "/usr/share/fonts/truetype/ubuntu/Ubuntu-R.ttf", size
            ),
        )

    def terminus_bold_16(self):
        return self._cached_font(
            "terminus_bold_16",
            lambda: ImageFont.load("/usr/share/fonts/X11/misc/ter-u16b_unicode.pil"),
        )

    def terminus_regular_12(self):
        return self._cached_font(
            "terminus_regular_12",
            lambda: ImageFont.load("/usr/share/fonts/X11/misc/ter-u12n_unicode.pil"),
        )

    def terminus_bold_14(self):
        return self._cached_font(
            "terminus_bold_14",
            lambda: ImageFont.load("/usr/share/fonts/X11/misc/ter-u14b_unicode.pil"),
        )

    def terminus_bold_22(self):
        return self._cached_font(
            "terminus_bold_22",
            lambda: ImageFont.load("/usr/share/fonts/X11/misc/ter-u22b_unicode.pil"),
        )


_default_font_loader = FontLoader()
ubuntu_regular = _default_font_loader.ubuntu_regular
terminus_bold_16 = _default_font_loader.terminus_bold_16
terminus_regular_12 = _default_font_loader.terminus_regular_12
terminus_bold_14 = _default_font_loader.terminus_bold_14
terminus_bold_22 = _default_font_loader.terminus_bold_22
