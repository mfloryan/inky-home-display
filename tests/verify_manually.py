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

import public_transport  # noqa: E402
from datetime import datetime  # noqa: E402

def test_get_morning_departures_concurrently():
    now = datetime(2025, 11, 8, 8, 0, 0)

    mock_responses = {
        2216: {"departures": [{"destination": "Danderyds sjukhus", "scheduled": "2025-11-08T08:17:36", "line": {"designation": "605", "transport_mode": "BUS"}, "journey": {"id": 123, "state": "EXPECTED"}, "stop_area": {"name": "Lahällsviadukten"}}]},
        9633: {"departures": [{"destination": "Stockholms östra", "scheduled": "2025-11-08T08:15:00", "line": {"designation": "27", "transport_mode": "TRAM"}, "journey": {"id": 456, "state": "NORMALPROGRESS"}, "stop_area": {"name": "Roslags Näsby"}}]}
    }

    def mocked_get(url):
        site_id = int(url.split("/")[-2])
        response = MagicMock()
        response.json.return_value = mock_responses.get(site_id, {"departures": []})
        return response

    with MagicMock() as mock_requests:
        sys.modules['requests'] = mock_requests
        mock_requests.get.side_effect = mocked_get
        # We need to re-import or update the reference in public_transport if it's already imported
        public_transport.requests = mock_requests

        departures = public_transport.get_morning_departures(now)

        assert len(departures) == 2
        assert departures[0]["stop_name"] == "Roslags Näsby"
        assert departures[1]["stop_name"] == "Lahällsviadukten"
        print("Test passed: get_morning_departures returns correct data.")

if __name__ == "__main__":
    sys.path.insert(0, "src")
    try:
        test_get_morning_departures_concurrently()
        print("Verification script completed successfully.")
    except Exception as e:
        print(f"Verification script failed: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
