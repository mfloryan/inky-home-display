import sys
from unittest.mock import MagicMock

# Mock all missing dependencies
mock_modules = [
    "requests",
    "PIL",
    "PIL.Image",
    "PIL.ImageFont",
    "PIL.ImageDraw",
    "inky",
    "inky.auto",
    "matplotlib",
    "matplotlib.pyplot",
    "numpy",
]

for module_name in mock_modules:
    sys.modules[module_name] = MagicMock()

# Now we can import pytest and run it
import pytest  # noqa: E402

if __name__ == "__main__":
    # Add src to path
    sys.path.insert(0, "src")

    # Run pytest
    # We might still get some errors if tests expect specific behavior from mocks,
    # but it's a start to see if our changes broke the basic logic.
    exit_code = pytest.main(["tests/test_public_transport.py"])
    sys.exit(exit_code)
