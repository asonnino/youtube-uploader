"""Unit tests for upload functions."""

import json
import os
import sys
from unittest import TestCase
from unittest.mock import Mock, patch, MagicMock, call
import pytest

# Import the module to test
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from upload import upload_video, main


class TestUpload(TestCase):
    """Test cases for video upload functionality."""

    def setUp(self):
        """Set up test fixtures."""
        self.test_video_file = "test_video.mp4"
        self.test_metadata_file = os.path.join(
            os.path.dirname(__file__), "fixtures", "test_metadata.json"
        )

        # Load test metadata
        with open(self.test_metadata_file, "r") as f:
            self.test_metadata = json.load(f)

    @patch("upload.MediaFileUpload")
    @patch("builtins.print")
    @patch("sys.stdout")
    def test_upload_video_success(self, mock_stdout, mock_print, mock_media_upload):
        """Test successful video upload."""
        # Create mock YouTube service
        mock_youtube = Mock()
        mock_request = Mock()
        mock_youtube.videos().insert.return_value = mock_request

        # Mock the upload progress
        mock_status = Mock()
        mock_status.progress.return_value = 0.5  # 50% progress

        # Mock response
        mock_response = {"id": "test_video_id", "status": {"uploadStatus": "uploaded"}}

        # Configure next_chunk to return progress once, then completed
        mock_request.next_chunk.side_effect = [
            (mock_status, None),  # First call - in progress
            (None, mock_response),  # Second call - completed
        ]

        # Call upload_video
        upload_video(mock_youtube, self.test_video_file, self.test_metadata_file)

        # Assert YouTube API was called correctly
        mock_youtube.videos().insert.assert_called_once_with(
            part="snippet,status",
            body=self.test_metadata,
            media_body=mock_media_upload.return_value,
        )

        # Assert MediaFileUpload was called with resumable=True
        mock_media_upload.assert_called_once_with(self.test_video_file, resumable=True)

        # Assert progress was displayed
        mock_stdout.write.assert_called()
        mock_stdout.flush.assert_called()

        # Assert success message was printed
        print_calls = mock_print.call_args_list
        self.assertTrue(any("Upload successful" in str(call) for call in print_calls))

    @patch("upload.MediaFileUpload")
    def test_upload_video_with_metadata_loading(self, mock_media_upload):
        """Test that metadata is correctly loaded from file."""
        # Create mock YouTube service
        mock_youtube = Mock()
        mock_request = Mock()
        mock_youtube.videos().insert.return_value = mock_request

        # Mock immediate success response
        mock_request.next_chunk.return_value = (None, {"id": "test_id"})

        # Call upload_video
        with patch("builtins.print"):
            upload_video(mock_youtube, self.test_video_file, self.test_metadata_file)

        # Get the actual call arguments
        call_kwargs = mock_youtube.videos().insert.call_args.kwargs

        # Assert metadata was loaded correctly
        self.assertEqual(call_kwargs["body"]["snippet"]["title"], "Test Video Title")
        self.assertEqual(call_kwargs["body"]["status"]["privacyStatus"], "private")

    def test_upload_video_missing_metadata_file(self):
        """Test handling of missing metadata file."""
        mock_youtube = Mock()

        # Call with non-existent metadata file
        with self.assertRaises(FileNotFoundError):
            upload_video(mock_youtube, self.test_video_file, "nonexistent.json")

    @patch("upload.MediaFileUpload")
    @patch("builtins.print")
    def test_upload_progress_tracking(self, mock_print, mock_media_upload):
        """Test that upload progress is tracked correctly."""
        # Create mock YouTube service
        mock_youtube = Mock()
        mock_request = Mock()
        mock_youtube.videos().insert.return_value = mock_request

        # Mock multiple progress updates
        progress_values = [0.25, 0.5, 0.75, 1.0]
        side_effects = []

        for progress in progress_values[:-1]:
            mock_status = Mock()
            mock_status.progress.return_value = progress
            side_effects.append((mock_status, None))

        # Final response
        side_effects.append((None, {"id": "test_id"}))
        mock_request.next_chunk.side_effect = side_effects

        # Call upload_video
        with patch("sys.stdout"):
            upload_video(mock_youtube, self.test_video_file, self.test_metadata_file)

        # Assert next_chunk was called multiple times
        self.assertEqual(mock_request.next_chunk.call_count, len(side_effects))


class TestMain(TestCase):
    """Test cases for main function and CLI."""

    @patch("upload.upload_video")
    @patch("upload.get_authenticated_service")
    @patch("upload.load_dotenv")
    @patch("os.getenv")
    def test_main_with_valid_arguments(
        self, mock_getenv, mock_load_dotenv, mock_get_auth, mock_upload
    ):
        """Test main function with valid command line arguments."""
        # Setup environment
        mock_getenv.return_value = "client_secret.json"
        mock_youtube = Mock()
        mock_get_auth.return_value = mock_youtube

        # Mock command line arguments
        test_args = ["upload.py", "video.mp4", "metadata.json"]
        with patch("sys.argv", test_args):
            main()

        # Assert functions were called
        mock_load_dotenv.assert_called_once()
        mock_get_auth.assert_called_once_with(
            "client_secret.json", use_device_flow=False
        )
        mock_upload.assert_called_once_with(mock_youtube, "video.mp4", "metadata.json")

    @patch("upload.upload_video")
    @patch("upload.get_authenticated_service")
    @patch("upload.load_dotenv")
    @patch("os.getenv")
    def test_main_with_device_auth(
        self, mock_getenv, mock_load_dotenv, mock_get_auth, mock_upload
    ):
        """Test main function with --device-auth flag."""
        # Setup environment
        mock_getenv.return_value = "client_secret.json"
        mock_youtube = Mock()
        mock_get_auth.return_value = mock_youtube

        # Mock command line arguments with device auth
        test_args = ["upload.py", "video.mp4", "metadata.json", "--device-auth"]
        with patch("sys.argv", test_args):
            main()

        # Assert device flow was used
        mock_get_auth.assert_called_once_with(
            "client_secret.json", use_device_flow=True
        )

    @patch("upload.load_dotenv")
    @patch("os.getenv")
    def test_main_missing_client_secret_env(self, mock_getenv, mock_load_dotenv):
        """Test main function when CLIENT_SECRET_FILE is not set."""
        # Setup environment without CLIENT_SECRET_FILE
        mock_getenv.return_value = None

        # Mock command line arguments
        test_args = ["upload.py", "video.mp4", "metadata.json"]
        with patch("sys.argv", test_args):
            with self.assertRaises(RuntimeError) as context:
                main()

            self.assertIn("CLIENT_SECRET_FILE not set", str(context.exception))

    @patch("sys.argv", ["upload.py", "--help"])
    def test_main_help_argument(self):
        """Test that help argument works."""
        with self.assertRaises(SystemExit) as context:
            with patch("sys.stdout"):
                main()

        # Help should exit with code 0
        self.assertEqual(context.exception.code, 0)

    @patch("sys.argv", ["upload.py"])  # Missing required arguments
    def test_main_missing_arguments(self):
        """Test main function with missing required arguments."""
        with self.assertRaises(SystemExit) as context:
            with patch("sys.stderr"):
                main()

        # Should exit with error code
        self.assertNotEqual(context.exception.code, 0)


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
