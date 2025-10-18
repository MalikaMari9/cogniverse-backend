import os
from pathlib import Path

# Base directory of the project
BASE_DIR = Path(__file__).resolve().parent.parent.parent

# Profile images directory
PROFILE_IMAGES_DIR = BASE_DIR / "static" / "profile_images"

# Create directory if it doesn't exist
PROFILE_IMAGES_DIR.mkdir(parents=True, exist_ok=True)

# Allowed file types
ALLOWED_IMAGE_TYPES = {
    "image/jpeg": "jpg",
    "image/png": "png",
    "image/gif": "gif",
    "image/webp": "webp"
}

# Max file size (5MB)
MAX_FILE_SIZE = 5 * 1024 * 1024

# Base URL for serving static files
PROFILE_IMAGE_BASE_URL = "/static/profile_images"