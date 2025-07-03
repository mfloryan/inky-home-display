"""Font loading functions for the display."""

from PIL import ImageFont

# Simple font cache
_font_cache = {}


def ubuntu_regular(size):
    """Ubuntu Regular font with specified size."""
    cache_key = f"ubuntu_regular_{size}"
    if cache_key not in _font_cache:
        _font_cache[cache_key] = ImageFont.truetype("/usr/share/fonts/truetype/ubuntu/Ubuntu-R.ttf", size)
    return _font_cache[cache_key]


def terminus_bold_16():
    """Terminus Bold 16pt font."""
    return ImageFont.load('/usr/share/fonts/X11/misc/ter-u16b_unicode.pil')


def terminus_regular_12():
    """Terminus Regular 12pt font."""
    return ImageFont.load('/usr/share/fonts/X11/misc/ter-u12n_unicode.pil')


def terminus_bold_14():
    """Terminus Bold 14pt font."""
    return ImageFont.load('/usr/share/fonts/X11/misc/ter-u14b_unicode.pil')


def terminus_bold_22():
    """Terminus Bold 22pt font."""
    return ImageFont.load('/usr/share/fonts/X11/misc/ter-u22b_unicode.pil')
