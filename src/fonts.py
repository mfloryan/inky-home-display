"""Font loading functions for the display."""

from PIL import ImageFont


def ubuntu_regular_22():
    """Ubuntu Regular 22pt font."""
    return ImageFont.truetype("/usr/share/fonts/truetype/ubuntu/Ubuntu-R.ttf", 22)


def ubuntu_regular_12():
    """Ubuntu Regular 12pt font."""
    return ImageFont.truetype("/usr/share/fonts/truetype/ubuntu/Ubuntu-R.ttf", 12)


def ubuntu_regular_11():
    """Ubuntu Regular 11pt font."""
    return ImageFont.truetype("/usr/share/fonts/truetype/ubuntu/Ubuntu-R.ttf", 11)


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
