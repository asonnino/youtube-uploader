"""Unit tests for upload functions."""

import json
import os
import sys
from unittest import TestCase
from unittest.mock import Mock, patch

import pytest
from googleapiclient.errors import ResumableUploadError

# Import the module to test
from youtube_uploader.main import main, upload_video


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

    @patch("youtube_uploader.main.MediaFileUpload")
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
        self.assertTrue(any("Upload successful" in str(c) for c in print_calls))

    @patch("youtube_uploader.main.MediaFileUpload")
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

        # Verify mock was used
        _ = mock_media_upload

    def test_upload_video_missing_metadata_file(self):
        """Test handling of missing metadata file."""
        mock_youtube = Mock()

        # Call with non-existent metadata file
        with self.assertRaises(FileNotFoundError):
            upload_video(mock_youtube, self.test_video_file, "nonexistent.json")

    @patch("youtube_uploader.main.MediaFileUpload")
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

        # Verify mocks were used
        _ = mock_print, mock_media_upload

    @patch("youtube_uploader.main.MediaFileUpload")
    @patch("builtins.print")
    @patch("sys.exit")
    def test_upload_video_youtube_signup_required(
        self, mock_exit, mock_print, mock_media_upload
    ):
        """Test handling of youtubeSignupRequired error."""
        # Create mock YouTube service
        mock_youtube = Mock()
        mock_request = Mock()
        mock_youtube.videos().insert.return_value = mock_request

        # Mock ResumableUploadError with youtubeSignupRequired
        error_content = (
            b"[{"
            b'"message": "Unauthorized", '
            b'"domain": "youtube.header", '
            b'"reason": "youtubeSignupRequired"'
            b"}]"
        )
        upload_error = ResumableUploadError(Mock(status=401), error_content)
        mock_request.next_chunk.side_effect = upload_error

        # Call upload_video
        upload_video(mock_youtube, self.test_video_file, self.test_metadata_file)

        # Assert error handling was called
        mock_exit.assert_called_once_with(1)

        # Check that appropriate error messages were printed
        print_calls = [str(call) for call in mock_print.call_args_list]
        self.assertTrue(any("Upload failed" in call for call in print_calls))
        self.assertTrue(any("YouTube channel" in call for call in print_calls))

        # Verify mock was used
        _ = mock_media_upload


class TestMain(TestCase):
    """Test cases for main function and CLI."""

    @patch("youtube_uploader.main.upload_video")
    @patch("youtube_uploader.main.get_authenticated_service")
    def test_main_with_valid_arguments(self, mock_get_auth, mock_upload):
        """Test main function with valid command line arguments."""
        mock_youtube = Mock()
        mock_get_auth.return_value = mock_youtube

        # Mock command line arguments
        test_args = [
            "youtube-uploader",
            "--video-file",
            "video.mp4",
            "--metadata-file",
            "metadata.json",
            "--client-secret",
            "client_secret.json",
        ]
        with patch("sys.argv", test_args):
            with patch("youtube_uploader.main.os.path.exists", return_value=True):
                main()

        # Assert functions were called
        mock_get_auth.assert_called_once_with("client_secret.json")
        mock_upload.assert_called_once_with(mock_youtube, "video.mp4", "metadata.json")

        # Removed test_main_with_device_auth as --device-auth flag was removed

        # Verify mocks were used
        _ = mock_upload

    def test_main_missing_client_secret_file(self):
        """Test main function when client secret file doesn't exist."""
        # Mock command line arguments
        test_args = [
            "youtube-uploader",
            "--video-file",
            "video.mp4",
            "--metadata-file",
            "metadata.json",
            "--client-secret",
            "nonexistent.json",
        ]
        with patch("sys.argv", test_args):
            with patch("youtube_uploader.main.os.path.exists", return_value=False):
                with self.assertRaises(FileNotFoundError) as context:
                    main()

                self.assertIn("Client secret file not found", str(context.exception))

    @patch("sys.argv", ["youtube-uploader", "--help"])
    def test_main_help_argument(self):
        """Test that help argument works."""
        with self.assertRaises(SystemExit) as context:
            with patch("sys.stdout"):
                main()

        # Help should exit with code 0
        self.assertEqual(context.exception.code, 0)

    def test_main_missing_client_secret_argument(self):
        """Test main function when --client-secret argument is missing."""
        # Mock command line arguments without --client-secret
        test_args = [
            "youtube-uploader",
            "--video-file",
            "video.mp4",
            "--metadata-file",
            "metadata.json",
        ]
        with patch("sys.argv", test_args):
            with self.assertRaises(SystemExit) as context:
                with patch("sys.stderr"):
                    main()

            # Should exit with error code
            self.assertNotEqual(context.exception.code, 0)

    @patch(
        "sys.argv", ["youtube-uploader", "--client-secret", "client_secret.json"]
    )  # Missing required arguments
    def test_main_missing_arguments(self):
        """Test main function with missing required arguments."""
        with self.assertRaises(SystemExit) as context:
            with patch("sys.stderr"):
                main()

        # Should exit with error code
        self.assertNotEqual(context.exception.code, 0)


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
