"""Cloudinary media upload service."""

from __future__ import annotations

import os
from typing import Any

import cloudinary
import cloudinary.uploader
from fastapi import HTTPException, UploadFile, status

from app.core.config import settings

# Configure Cloudinary using environment variables / application settings
cloudinary.config(
    cloud_name=settings.CLOUDINARY_CLOUD_NAME or os.getenv("CLOUDINARY_CLOUD_NAME"),
    api_key=settings.CLOUDINARY_API_KEY or os.getenv("CLOUDINARY_API_KEY"),
    api_secret=settings.CLOUDINARY_API_SECRET or os.getenv("CLOUDINARY_API_SECRET"),
    secure=True,
)

ALLOWED_IMAGE_TYPES = {"image/jpeg", "image/png", "image/webp"}
MAX_IMAGE_SIZE_BYTES = 5 * 1024 * 1024  # 5 MB


def validate_image_file(file: UploadFile) -> None:
    """Validate MIME type and size of uploaded image."""
    if file.content_type not in ALLOWED_IMAGE_TYPES:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=(
                f"Unsupported image type: {file.content_type}. "
                f"Allowed types: {', '.join(sorted(ALLOWED_IMAGE_TYPES))}"
            ),
        )

    if file.size is not None and file.size > MAX_IMAGE_SIZE_BYTES:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Image size exceeds maximum limit of 5 MB ({file.size} bytes provided).",
        )


async def upload_image_to_cloudinary(
    file: UploadFile,
    folder: str = "club-management/events",
) -> str:
    """Upload an image file directly to Cloudinary and return its secure URL."""
    validate_image_file(file)

    try:
        await file.seek(0)
        content = await file.read()
        if len(content) > MAX_IMAGE_SIZE_BYTES:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Image size exceeds maximum limit of 5 MB ({len(content)} bytes provided).",
            )

        result: dict[str, Any] = cloudinary.uploader.upload(
            content,
            folder=folder,
            resource_type="image",
        )

        secure_url = result.get("secure_url")
        if not secure_url:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Cloudinary upload succeeded but secure_url was not returned",
            )
        return str(secure_url)

    except HTTPException:
        raise
    except Exception as exc:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to upload image to Cloudinary: {exc!s}",
        ) from exc
    finally:
        await file.close()