import json
from cache import cache, DateTimeEncoder, datetime_decoder
from unittest.mock import patch
from datetime import datetime

class TestCacheFunction:
    def test_should_return_cached_data_when_cache_file_exists(self, tmp_path):
        # Arrange
        cached_data ={"temperature": 25, "humidity": 60}
        cache_file_path = tmp_path / "weather_data.json"
        cache_file_path.write_text(json.dumps(cached_data))

        def expensive_operation():
            return {"temperature": 30, "humidity": 70}

        # Act
        with patch("cache.os.path.join", return_value=str(cache_file_path)):
            result = cache("weather_data", expensive_operation)

        # Assert
        assert result == cached_data

    def test_should_execute_operation_and_return_fresh_data_when_cache_file_missing(
        self, tmp_path
    ):
        # Arrange
        fresh_data = {"temperature": 28, "humidity": 65}
        nonexistent_cache_path = tmp_path / "missing_cache.json"

        def data_fetching_operation():
            return fresh_data

        # Act
        with patch("cache.os.path.join", return_value=str(nonexistent_cache_path)):
            with patch("cache.os.mkdir"):
                result = cache("missing_cache", data_fetching_operation)

        # Assert
        assert result == fresh_data

    def test_should_create_cache_directory_and_file_physically(self, tmp_path):
        # Arrange
        fake_cache_dir = tmp_path / "subdir" / "cache"
        cache_key = "test_item"
        expected_file = fake_cache_dir / f"{cache_key}.json"

        data = {"key": "value"}

        # We patch the module's internal path construction to point to our tmp_path
        # but we let the actual os.makedirs and open() calls happen.
        with patch("cache.os.path.join", return_value=str(expected_file)):
            # Act
            result = cache(cache_key, lambda: data)

        # Assert
        assert result == data
        assert fake_cache_dir.exists()
        assert expected_file.is_file()

    def test_should_save_operation_result_to_cache_file_when_successful(self, tmp_path):
        # Arrange
        operation_data = {"api_response": "data"}
        cache_file_path = tmp_path / "api_cache.json"

        def api_call():
            return operation_data

        # Act
        with patch("cache.os.path.join", return_value=str(cache_file_path)):
            with patch("cache.os.mkdir"):
                cache("api_cache", api_call)

        # Assert
        cache_content = json.loads(cache_file_path.read_text())
        assert cache_content == operation_data

    def test_should_not_save_empty_array_to_cache_file(self, tmp_path):
        # Arrange
        cache_file_path = tmp_path / "empty_cache.json"

        def operation_returning_empty_array():
            return []

        # Act
        with patch("cache.os.path.join", return_value=str(cache_file_path)):
            with patch("cache.os.mkdir"):
                result = cache("empty_cache", operation_returning_empty_array)

        # Assert
        assert result == []
        assert not cache_file_path.exists()

    def test_should_handle_exception_during_cache_write_gracefully(self, tmp_path):
        # Arrange
        operation_data = {"status": "ok"}
        cache_file_path = tmp_path / "fail_cache.json"

        def some_operation():
            return operation_data

        # Act
        with patch("cache.os.path.join", return_value=str(cache_file_path)):
            with patch("cache.os.mkdir", side_effect=OSError("Permission denied")):
                # This should not raise an exception
                result = cache("fail_cache", some_operation)

        # Assert
        assert result == operation_data

    def test_should_handle_corrupted_json_during_cache_read_gracefully(self, tmp_path):
        # Arrange
        cache_file_path = tmp_path / "corrupted_cache.json"
        cache_file_path.write_text("not a valid json")

        def some_operation():
            return {"status": "ok"}

        # Act
        with patch("cache.os.path.join", return_value=str(cache_file_path)):
            result = cache("corrupted_cache", some_operation)

        # Assert
        assert result == {"status": "ok"}

    def test_should_maintain_type_symmetry(self, tmp_path):
        # Arrange
        cache_key = "symmetry_test"
        cache_file_path = tmp_path / f"{cache_key}.json"

        # Data contains actual datetime objects
        test_date = datetime(2026, 4, 29, 9, 0)
        original_data = [{"stop_name": "Roslags Näsby", "time": test_date}]

        # Act
        with patch("cache.os.path.join", return_value=str(cache_file_path)):
            # 1. Populate cache
            _ = cache(cache_key, lambda: original_data)

            # 2. Retrieve from cache
            second_result = cache(cache_key, lambda: [])

        # Assert
        assert second_result == original_data
        assert isinstance(second_result[0]["time"], datetime)
        assert second_result[0]["time"].hour == 9