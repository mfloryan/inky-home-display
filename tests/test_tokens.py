import pytest
from unittest.mock import patch, mock_open
from tokens import read_token_file


def test_read_token_file_success():
    mock_content = "  my-secret-token  \n"
    with patch("builtins.open", mock_open(read_data=mock_content)):
        token = read_token_file("fake-token", "Error message")
        assert token == "my-secret-token"


def test_read_token_file_not_found():
    with patch("builtins.open", side_effect=FileNotFoundError()):
        with patch("tokens.logger") as mock_logger:
            with pytest.raises(RuntimeError, match="Custom error message"):
                read_token_file("non-existent", "Custom error message")

            mock_logger.error.assert_called_once_with(
                "Token file `%s` not found", "non-existent"
            )
