"""YouTube uploader package for command-line video uploads."""

__version__ = "1.0.0"
__author__ = "Your Name"
__email__ = "your.email@example.com"

from .main import get_authenticated_service, upload_video

__all__ = ["get_authenticated_service", "upload_video", "__version__"]
