from PIL import ImageFont


class FontLoader:
    def __init__(self):
        self._cache = {}

    def _cached_font(self, cache_key, loader_func):
        if cache_key not in self._cache:
            self._cache[cache_key] = loader_func()
        return self._cache[cache_key]

    def _make_terminus_bold(self, size):
        return ImageFont.truetype(
            "/usr/share/fonts/opentype/terminus/terminus-bold.otb", size
        )

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
            lambda: self._make_terminus_bold(16),
        )

    def terminus_regular_12(self):
        return self._cached_font(
            "terminus_regular_12",
            lambda: ImageFont.truetype(
                "/usr/share/fonts/opentype/terminus/terminus-normal.otb", 12
            ),
        )

    def terminus_bold_14(self):
        return self._cached_font(
            "terminus_bold_14",
            lambda: self._make_terminus_bold(14),
        )

    def terminus_bold_22(self):
        return self._cached_font(
            "terminus_bold_22",
            lambda: self._make_terminus_bold(22)
        )
