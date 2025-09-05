#!/usr/bin/env python3
"""YouTube video uploader script with OAuth authentication."""

import argparse
import json
import os
import pickle
import sys

from dotenv import load_dotenv
from google.auth.transport.requests import Request
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload

# YouTube upload scope - required permission for uploading videos
SCOPES = ["https://www.googleapis.com/auth/youtube.upload"]


def get_authenticated_service(
    client_secret_file, use_device_flow=False, token_file="token.pickle"
):
    """Authenticate and return YouTube service object.

    Args:
        client_secret_file: Path to OAuth2 client secret JSON file
        use_device_flow: If True, use device flow for headless authentication
        token_file: Path to store/load cached credentials

    Returns:
        Authenticated YouTube service object
    """
    credentials = None
    # Load existing credentials from file if available
    if os.path.exists(token_file):
        with open(token_file, "rb") as f:
            credentials = pickle.load(
                f
            )  # nosec B301 - pickle is safe here, we control the file

    # Check if credentials need to be obtained or refreshed
    if not credentials or not credentials.valid:
        if credentials and credentials.expired and credentials.refresh_token:
            # Refresh expired credentials using refresh token
            credentials.refresh(Request())
        else:
            # No valid credentials, need to authenticate
            if use_device_flow:
                # Device flow: displays a code to enter on another device
                # Useful for headless servers without browser access
                with open(client_secret_file, "r") as f:
                    client_config = json.load(f)
                flow = InstalledAppFlow.from_client_config(client_config, SCOPES)
                credentials = flow.run_console()  # Shows device code in terminal
            else:
                # Browser flow: opens local browser for authentication
                # Standard flow for desktop environments
                flow = InstalledAppFlow.from_client_secrets_file(
                    client_secret_file, SCOPES
                )
                credentials = flow.run_local_server(port=0)

        # Save credentials for future runs
        with open(token_file, "wb") as f:
            pickle.dump(credentials, f)

    # Build and return the YouTube API service object
    return build("youtube", "v3", credentials=credentials)


def upload_video(youtube, video_file, metadata_file):
    """Upload a video to YouTube with specified metadata.

    Args:
        youtube: Authenticated YouTube service object
        video_file: Path to video file to upload
        metadata_file: Path to JSON file containing video metadata
    """
    # Load video metadata from JSON file
    with open(metadata_file, "r") as f:
        metadata = json.load(f)

    # Create upload request with resumable upload for large files
    request = youtube.videos().insert(
        part="snippet,status",  # Include video details and privacy status
        body=metadata,
        media_body=MediaFileUpload(video_file, resumable=True),
    )

    # Upload the video with progress tracking
    print(f"⏳ Uploading {video_file} ...")
    response = None
    while response is None:
        status, response = request.next_chunk()
        if status:
            # Display upload progress
            percent = int(status.progress() * 100)
            sys.stdout.write(f"\rProgress: {percent}%")
            sys.stdout.flush()

    # Upload complete - display success and video details
    print("\n✅ Upload successful!")
    print(json.dumps(response, indent=2))


def main():
    """Handle command line arguments and orchestrate upload."""
    # Set up command line argument parser
    parser = argparse.ArgumentParser(description="Upload a video to YouTube via CLI.")
    parser.add_argument("video_file", help="Path to the video file")
    parser.add_argument("metadata_file", help="Path to JSON metadata file")
    parser.add_argument(
        "--device-auth",
        action="store_true",
        help="Use OAuth device/console flow (for headless servers)",
    )
    args = parser.parse_args()

    # Load environment variables from .env file
    load_dotenv()
    client_secret_file = os.getenv("CLIENT_SECRET_FILE")
    if not client_secret_file:
        raise RuntimeError("CLIENT_SECRET_FILE not set in .env")

    # Authenticate and get YouTube service
    youtube = get_authenticated_service(
        client_secret_file, use_device_flow=args.device_auth
    )

    # Upload the video with provided metadata
    upload_video(youtube, args.video_file, args.metadata_file)


if __name__ == "__main__":
    main()
