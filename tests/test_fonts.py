from unittest.mock import patch
from fonts import FontLoader


class TestFontLoader:
    @patch("fonts.ImageFont.truetype")
    def test_ubuntu_regular_should_cache_and_reuse_same_font(self, mock_truetype):
        font_loader = FontLoader()

        font_loader.ubuntu_regular(12)
        font_loader.ubuntu_regular(12)

        assert mock_truetype.call_count == 1

    @patch("fonts.ImageFont.truetype")
    def test_terminus_bold_16_should_cache_and_reuse_same_font(self, mock_truetype):
        font_loader = FontLoader()

        font1 = font_loader.terminus_bold_16()
        font2 = font_loader.terminus_bold_16()

        assert mock_truetype.call_count == 1
        assert font1 is font2
