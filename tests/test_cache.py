import json
from cache import cache
from unittest.mock import patch


class TestCacheFunction:
    def test_should_return_cached_data_when_cache_file_exists(self, tmp_path):
        # Arrange
        cached_data = {"temperature": 25, "humidity": 60}
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

    def test_should_create_cache_directory_when_it_does_not_exist(self, tmp_path):
        # Arrange
        operation_result = {"status": "success"}
        cache_dir = tmp_path / "cache"
        cache_file = cache_dir / "new_cache.json"

        def some_operation():
            return operation_result

        # Act
        with patch("cache.os.path.join", return_value=str(cache_file)):
            with patch("cache.os.path.exists", return_value=False):
                with patch("cache.os.mkdir") as mock_mkdir:
                    cache("new_cache", some_operation)

        # Assert
        mock_mkdir.assert_called_once()

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
