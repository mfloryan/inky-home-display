from unittest.mock import patch
from fonts import ubuntu_regular


class TestFontCaching:
    @patch('fonts.ImageFont.truetype')
    def test_ubuntu_regular_should_cache_and_reuse_same_font(self, mock_truetype):
        # Act - Call the same font twice
        ubuntu_regular(12)
        ubuntu_regular(12)
        
        # Assert - Font should only be loaded from disk once (target behavior)
        assert mock_truetype.call_count == 1