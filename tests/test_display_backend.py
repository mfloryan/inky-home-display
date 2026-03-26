import pytest
from unittest.mock import MagicMock, patch
import sys

# Mock PIL and inky before importing display_backend
mock_pil = MagicMock()
mock_inky = MagicMock()
sys.modules["PIL"] = mock_pil
sys.modules["PIL.Image"] = mock_pil.Image
sys.modules["inky"] = mock_inky
sys.modules["inky.auto"] = mock_inky.auto

from display_backend import PngFileBackend, InkyBackend, create_backend  # noqa: E402

class TestPngFileBackend:
    def test_resolution(self):
        backend = PngFileBackend()
        assert backend.resolution == (400, 300)

    def test_colors(self):
        backend = PngFileBackend()
        assert backend.colors == ((0, 0, 0), (220, 220, 0), (255, 255, 255))

    def test_create_image(self):
        backend = PngFileBackend()
        backend.create_image()
        mock_pil.Image.new.assert_called_with("P", size=(400, 300), color=(255, 255, 255))

    def test_show(self):
        output_path = "test.png"
        backend = PngFileBackend(output_path=output_path)
        img = MagicMock()
        backend.show(img)
        img.save.assert_called_once_with(output_path, format="PNG")


class TestInkyBackend:
    @patch("display_backend.InkyBackend.__init__", return_value=None)
    def test_properties(self, mock_init):
        backend = InkyBackend()
        backend.inky_display = MagicMock()
        backend.inky_display.resolution = (400, 300)
        backend.inky_display.BLACK = (0, 0, 0)
        backend.inky_display.YELLOW = (220, 220, 0)
        backend.inky_display.WHITE = (255, 255, 255)

        assert backend.resolution == (400, 300)
        assert backend.colors == ((0, 0, 0), (220, 220, 0), (255, 255, 255))

    @patch("display_backend.InkyBackend.__init__", return_value=None)
    def test_create_image(self, mock_init):
        backend = InkyBackend()
        backend.inky_display = MagicMock()
        backend.inky_display.resolution = (400, 300)

        backend.create_image()
        mock_pil.Image.new.assert_called_with("P", (400, 300))

    @patch("display_backend.InkyBackend.__init__", return_value=None)
    def test_show(self, mock_init):
        backend = InkyBackend()
        backend.inky_display = MagicMock()
        backend.inky_display.WHITE = 2

        img = MagicMock()
        backend.show(img)

        backend.inky_display.set_border.assert_called_once_with(2)
        backend.inky_display.set_image.assert_called_once_with(img)
        backend.inky_display.show.assert_called_once()

    def test_init_import_error(self):
        with patch("builtins.__import__", side_effect=ImportError):
            with pytest.raises(RuntimeError, match="inky library not available"):
                InkyBackend()

    def test_init_runtime_error(self):
        mock_auto = MagicMock(side_effect=RuntimeError("No display"))
        with patch.dict("sys.modules", {"inky.auto": MagicMock(auto=mock_auto)}):
            with pytest.raises(RuntimeError, match="No INKY display found: No display"):
                InkyBackend()


class TestCreateBackend:
    @patch("display_backend.InkyBackend")
    def test_create_backend_prefer_inky_success(self, mock_inky_class):
        mock_inky_instance = MagicMock(spec=InkyBackend)
        mock_inky_class.return_value = mock_inky_instance

        backend = create_backend(prefer_inky=True)

        assert backend == mock_inky_instance
        mock_inky_class.assert_called_once()

    @patch("display_backend.InkyBackend")
    def test_create_backend_prefer_inky_failure(self, mock_inky_class):
        mock_inky_class.side_effect = RuntimeError("Failed")

        backend = create_backend(prefer_inky=True)

        assert isinstance(backend, PngFileBackend)
        mock_inky_class.assert_called_once()

    def test_create_backend_no_inky(self):
        backend = create_backend(prefer_inky=False)
        assert isinstance(backend, PngFileBackend)

    def test_create_backend_custom_path(self):
        custom_path = "custom/path.png"
        backend = create_backend(prefer_inky=False, png_output_path=custom_path)
        assert isinstance(backend, PngFileBackend)
        assert backend.output_path == custom_path
