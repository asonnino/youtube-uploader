# YouTube Uploader

[![Tests](https://github.com/asonnino/youtube-uploader/actions/workflows/test.yml/badge.svg?branch=main)](https://github.com/asonnino/youtube-uploader/actions/workflows/test.yml)
[![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)
[![Python 3.9+](https://img.shields.io/badge/python-3.9%2B-blue.svg)](https://www.python.org/downloads/)
[![License](https://img.shields.io/badge/license-Apache%202.0-blue.svg)](https://opensource.org/licenses/Apache-2.0)

Simple Python script to upload YouTube videos from the command line.

## Setup

### 1. Install Dependencies

```bash
# Create virtual environment
python -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate

# Install required packages
pip install -r requirements.txt
```

### 2. Configure YouTube API Credentials

1. Go to [Google Cloud Console](https://console.cloud.google.com)
2. Create a new project or select an existing one
3. Enable YouTube Data API v3
4. Create OAuth 2.0 credentials (Desktop application type)
5. Download the client secret JSON file

### 3. Set Environment Variables

```bash
# Copy the example environment file
cp .env.example .env

# Edit .env and set the path to your client secret JSON file
CLIENT_SECRET_FILE=path/to/your/client_secret.json
```

## Usage

```bash
# Basic upload
python upload.py video.mp4 metadata.json

# For headless servers (no browser available)
python upload.py video.mp4 metadata.json --device-auth
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
