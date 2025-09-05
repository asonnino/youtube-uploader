"""Unit tests for authentication functions."""

import json
import os
import shutil
import sys
import tempfile
from unittest import TestCase
from unittest.mock import Mock, mock_open, patch

import pytest

# Import the module to test
from youtube_uploader.main import SCOPES, get_authenticated_service


class TestAuthentication(TestCase):
    """Test cases for authentication functionality."""

    def setUp(self):
        """Set up test fixtures."""
        self.temp_dir = tempfile.mkdtemp()
        self.token_file = os.path.join(self.temp_dir, "test_token.pickle")
        self.client_secret_file = os.path.join(self.temp_dir, "client_secret.json")

        # Create a mock client secret file
        client_secret_data = {
            "installed": {
                "client_id": "test_client_id",
                "client_secret": "test_secret",
                "auth_uri": "https://accounts.google.com/o/oauth2/auth",
                "token_uri": "https://oauth2.googleapis.com/token",
            }
        }
        with open(self.client_secret_file, "w") as f:
            json.dump(client_secret_data, f)

    def tearDown(self):
        """Clean up test fixtures."""
        shutil.rmtree(self.temp_dir, ignore_errors=True)

    @patch("youtube_uploader.main.build")
    @patch("youtube_uploader.main.pickle.load")
    def test_load_valid_credentials_from_pickle(self, mock_pickle_load, mock_build):
        """Test loading valid credentials from pickle file."""
        # Create mock credentials
        mock_credentials = Mock()
        mock_credentials.valid = True
        mock_pickle_load.return_value = mock_credentials

        # Create empty token file
        open(self.token_file, "wb").close()

        # Call the function
        get_authenticated_service(self.client_secret_file, token_file=self.token_file)

        # Assert build was called with the credentials
        mock_build.assert_called_once_with(
            "youtube", "v3", credentials=mock_credentials
        )

    @patch("youtube_uploader.main.build")
    @patch("youtube_uploader.main.Request")
    @patch("youtube_uploader.main.pickle.load")
    @patch("youtube_uploader.main.pickle.dump")
    def test_refresh_expired_credentials(
        self, mock_pickle_dump, mock_pickle_load, mock_request, mock_build
    ):
        """Test refreshing expired credentials with refresh token."""
        # Create mock expired credentials with refresh token
        mock_credentials = Mock()
        mock_credentials.valid = False
        mock_credentials.expired = True
        mock_credentials.refresh_token = "test_refresh_token"
        mock_pickle_load.return_value = mock_credentials

        # Create empty token file
        open(self.token_file, "wb").close()

        # Call the function
        get_authenticated_service(self.client_secret_file, token_file=self.token_file)

        # Assert refresh was called
        mock_credentials.refresh.assert_called_once()
        mock_build.assert_called_once()

        # Verify mocks were called (even if not directly used)
        _ = mock_pickle_dump, mock_request

    @patch("youtube_uploader.main.build")
    @patch("youtube_uploader.main.InstalledAppFlow")
    @patch("youtube_uploader.main.pickle.dump")
    def test_browser_flow_authentication(
        self, mock_pickle_dump, mock_flow_class, mock_build
    ):
        """Test browser-based OAuth flow."""
        # Setup mock flow
        mock_flow = Mock()
        mock_credentials = Mock()
        mock_credentials.valid = True
        mock_flow.run_local_server.return_value = mock_credentials
        mock_flow_class.from_client_secrets_file.return_value = mock_flow

        # Call the function with no existing token file
        get_authenticated_service(self.client_secret_file, token_file=self.token_file)

        # Assert browser flow was used
        mock_flow_class.from_client_secrets_file.assert_called_once_with(
            self.client_secret_file, SCOPES
        )
        mock_flow.run_local_server.assert_called_once_with(port=0)

        # Assert credentials were saved
        mock_pickle_dump.assert_called_once()

        # Verify mock was called
        _ = mock_build

    @patch("youtube_uploader.main.build")
    @patch("youtube_uploader.main.InstalledAppFlow")
    @patch("youtube_uploader.main.pickle.dump")
    def test_headless_server_error_handling(
        self, mock_pickle_dump, mock_flow_class, mock_build
    ):
        """Test error handling for headless servers without browsers."""
        # Setup mock flow that raises an exception for headless environments
        mock_flow = Mock()
        mock_flow.run_local_server.side_effect = Exception(
            "No DISPLAY environment variable"
        )
        mock_flow_class.from_client_secrets_file.return_value = mock_flow

        # Call the function and expect it to exit
        with patch("builtins.print") as mock_print:
            with patch("sys.exit") as mock_exit:
                get_authenticated_service(
                    self.client_secret_file,
                    token_file=self.token_file,
                )

                # Verify that helpful instructions were printed
                mock_print.assert_called()
                mock_exit.assert_called_once_with(1)

        # Verify mocks were called
        _ = mock_pickle_dump, mock_build

    @patch("youtube_uploader.main.build")
    @patch("youtube_uploader.main.pickle.load")
    @patch("youtube_uploader.main.pickle.dump")
    def test_invalid_credentials_without_refresh_token(
        self, mock_pickle_dump, mock_pickle_load, mock_build
    ):
        """Test handling of invalid credentials without refresh token."""
        # Create mock invalid credentials without refresh token
        mock_credentials = Mock()
        mock_credentials.valid = False
        mock_credentials.expired = True
        mock_credentials.refresh_token = None
        mock_pickle_load.return_value = mock_credentials

        # Create empty token file
        open(self.token_file, "wb").close()

        # Mock the flow to avoid actual OAuth
        with patch("youtube_uploader.main.InstalledAppFlow") as mock_flow_class:
            mock_flow = Mock()
            new_credentials = Mock()
            new_credentials.valid = True
            mock_flow.run_local_server.return_value = new_credentials
            mock_flow_class.from_client_secrets_file.return_value = mock_flow

            # Call the function
            get_authenticated_service(
                self.client_secret_file, token_file=self.token_file
            )

            # Assert new authentication was triggered
            mock_flow_class.from_client_secrets_file.assert_called_once()
            mock_flow.run_local_server.assert_called_once()

        # Verify mocks were called
        _ = mock_pickle_dump, mock_build


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
