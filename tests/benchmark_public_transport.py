import time
from datetime import datetime
from unittest.mock import patch, Mock

# Mocking the missing dependencies for the purpose of the benchmark
import sys
sys.modules['requests'] = Mock()
sys.modules['cache'] = Mock()

from public_transport import get_morning_departures

def mocked_requests_get(*args, **kwargs):
    time.sleep(0.5)  # Simulate 500ms network latency
    mock_response = Mock()
    mock_response.json.return_value = {"departures": []}
    return mock_response

def run_benchmark():
    now = datetime(2025, 11, 8, 8, 0, 0)

    with patch("public_transport.requests.get", side_effect=mocked_requests_get):
        start_time = time.time()
        get_morning_departures(now)
        end_time = time.time()

    duration = end_time - start_time
    print(f"Time taken: {duration:.4f} seconds")
    return duration

if __name__ == "__main__":
    print("Running baseline benchmark...")
    durations = [run_benchmark() for _ in range(5)]
    average_duration = sum(durations) / len(durations)
    print(f"Average time taken: {average_duration:.4f} seconds")
