# YouTube Uploader

[![Tests](https://github.com/asonnino/youtube-uploader/actions/workflows/test.yml/badge.svg?branch=main)](https://github.com/asonnino/youtube-uploader/actions/workflows/test.yml)
[![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)
[![Python 3.9+](https://img.shields.io/badge/python-3.9%2B-blue.svg)](https://www.python.org/downloads/)
[![License](https://img.shields.io/badge/license-Apache%202.0-blue.svg)](https://opensource.org/licenses/Apache-2.0)

Simple Python script to upload YouTube videos from the command line.

## Installation

### Option 1: pipx (Recommended)

Install using [pipx](https://pypa.github.io/pipx/) for isolated dependency management:

```bash
# Install from local directory
pipx install .

# Or install directly from GitHub
pipx install git+https://github.com/asonnino/youtube-uploader.git
```

### Option 2: Manual Setup

```bash
# Create virtual environment
python -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate

# Install required packages
pip install -r requirements.txt
```

## Setup

### 1. Configure YouTube API Credentials

1. Go to [Google Cloud Console](https://console.cloud.google.com)
2. Create a new project or select an existing one
3. Enable YouTube Data API v3
4. Create OAuth 2.0 credentials (Desktop application type)
5. Download the client secret JSON file

### 2. YouTube Channel Requirement

**Important:** Your Google account must have a YouTube channel to upload videos. If you get a `youtubeSignupRequired` error:

1. Visit [YouTube.com](https://youtube.com)
2. Sign in with your Google account
3. Create a YouTube channel if you don't have one
4. Try uploading again

## Usage

### With pipx installation

```bash
# Basic upload
youtube-uploader --video-file video.mp4 --metadata-file metadata.json --client-secret client_secret.json

# For headless servers (displays URL to visit manually)
youtube-uploader --video-file video.mp4 --metadata-file metadata.json --client-secret client_secret.json --device-auth
```

### With manual setup

```bash
# Basic upload
python youtube_uploader/main.py --video-file video.mp4 --metadata-file metadata.json --client-secret client_secret.json

# For headless servers (displays URL to visit manually)
python youtube_uploader/main.py --video-file video.mp4 --metadata-file metadata.json --client-secret client_secret.json --device-auth
```

### Metadata File Format

See `tests/fixtures/test_metadata.json` for an example. Create a JSON file with:

```json
{
  "snippet": {
    "title": "Your Video Title",
    "description": "Your video description",
    "tags": ["tag1", "tag2"],
    "categoryId": "22"
  },
  "status": {
    "privacyStatus": "private"
  }
}
```

Privacy options: `"private"`, `"unlisted"`, `"public"`

## Troubleshooting

### Common Errors

**`youtubeSignupRequired`**: Your Google account needs a YouTube channel
- Visit [YouTube.com](https://youtube.com) and create a channel
- Try uploading again

**`quotaExceeded`**: API quota limit reached
- Wait and try again later
- Consider requesting quota increase in Google Cloud Console

**Authentication Issues**:
- Ensure OAuth credentials have YouTube upload permissions
- Check that client secret file is valid and accessible
- For headless servers, use `--device-auth` flag

## Testing

```bash
# Install development dependencies
pip install -r requirements-dev.txt

# Run tests with coverage report
pytest --cov=upload --cov-report=term-missing

# Generate HTML coverage report
pytest --cov=upload --cov-report=html
# Open htmlcov/index.html in your browser
```

## License

This project is licensed under the Apache License 2.0 - see the [LICENSE](LICENSE) file for details.
