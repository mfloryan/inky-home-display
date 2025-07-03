from unittest.mock import patch
from fonts import ubuntu_regular, terminus_bold_16


class TestFontCaching:
    @patch('fonts.ImageFont.truetype')
    def test_ubuntu_regular_should_cache_and_reuse_same_font(self, mock_truetype):
        # Act - Call the same font twice
        ubuntu_regular(12)
        ubuntu_regular(12)
        
        # Assert - Font should only be loaded from disk once (target behavior)
        assert mock_truetype.call_count == 1

    @patch('fonts.ImageFont.load')
    def test_terminus_bold_16_should_cache_and_reuse_same_font(self, mock_load):
        # Act - Call the same font twice
        font1 = terminus_bold_16()
        font2 = terminus_bold_16()
        
        # Assert - Font should only be loaded from disk once AND same object reused
        assert mock_load.call_count == 1
        assert font1 is font2