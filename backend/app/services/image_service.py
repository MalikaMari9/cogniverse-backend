import os
import uuid
from fastapi import UploadFile

UPLOAD_DIR = "uploads/profile_images"

os.makedirs(UPLOAD_DIR, exist_ok=True)

def upload_image_to_s3(file: UploadFile) -> str:
    # simulate upload
    file_extension = os.path.splitext(file.filename)[1]
    filename = f"{uuid.uuid4()}{file_extension}"
    file_path = os.path.join(UPLOAD_DIR, filename)
    with open(file_path, "wb") as f:
        f.write(file.file.read())
    return f"/{UPLOAD_DIR}/{filename}"
