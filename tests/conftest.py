import sys
from unittest.mock import MagicMock

# Mock external dependencies that might be missing in the environment
mock_requests = MagicMock()
mock_requests.exceptions.Timeout = type("Timeout", (Exception,), {})
mock_requests.exceptions.RequestException = type("RequestException", (Exception,), {})
sys.modules["requests"] = mock_requests
sys.modules["inky"] = MagicMock()
sys.modules["PIL"] = MagicMock()
sys.modules["PIL.Image"] = MagicMock()
sys.modules["PIL.ImageDraw"] = MagicMock()
sys.modules["PIL.ImageFont"] = MagicMock()
sys.modules["numpy"] = MagicMock()
