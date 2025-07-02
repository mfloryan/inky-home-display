"""Display backend abstraction for different output methods."""

from abc import ABC, abstractmethod
from PIL import Image, ImageDraw


class DisplayBackend(ABC):
    """Abstract base class for display backends."""
    
    @property
    @abstractmethod
    def resolution(self):
        """Return display resolution as (width, height) tuple."""
        pass
    
    @property
    @abstractmethod
    def colors(self):
        """Return color palette as (black, yellow, white) tuple."""
        pass
    
    @abstractmethod
    def create_image(self):
        """Create and return a PIL Image for drawing."""
        pass
    
    @abstractmethod
    def show(self, image):
        """Display the given image on the output device."""
        pass


class PngFileBackend(DisplayBackend):
    """Backend that saves output as PNG file."""
    
    def __init__(self, output_path="img/test.png"):
        self.output_path = output_path
    
    @property
    def resolution(self):
        return (400, 300)
    
    @property
    def colors(self):
        return ((0, 0, 0), (220, 220, 0), (255, 255, 255))
    
    def create_image(self):
        return Image.new("P", size=self.resolution, color=(255, 255, 255))
    
    def show(self, image):
        image.save(self.output_path, format="PNG")
        print(f"Image saved to {self.output_path}")


class InkyBackend(DisplayBackend):
    """Backend for Pimoroni Inky display hardware."""
    
    def __init__(self):
        try:
            from inky.auto import auto
            self.inky_display = auto()
            print(f"INKY wHat display: {self.inky_display.colour}")
        except ImportError:
            raise RuntimeError("inky library not available")
        except RuntimeError as e:
            raise RuntimeError(f"No INKY display found: {e}")
    
    @property
    def resolution(self):
        return self.inky_display.resolution
    
    @property
    def colors(self):
        return (self.inky_display.BLACK, self.inky_display.YELLOW, self.inky_display.WHITE)
    
    def create_image(self):
        return Image.new("P", self.resolution)
    
    def show(self, image):
        self.inky_display.set_border(self.inky_display.WHITE)
        self.inky_display.set_image(image)
        self.inky_display.show()


def create_backend(prefer_inky=True, png_output_path="img/test.png"):
    """Create the appropriate display backend based on availability."""
    
    if prefer_inky:
        try:
            return InkyBackend()
        except (ImportError, RuntimeError) as e:
            print(f"Could not initialize Inky backend: {e}")
            print("Falling back to PNG file output")
    
    return PngFileBackend(png_output_path)