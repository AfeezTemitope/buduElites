"""
Cloudinary upload service.
Implements Blob Storage + CDN pattern.
"""
import logging
import cloudinary.uploader

logger = logging.getLogger("befa.cloudinary")


def upload_image(file, folder="befa", **kwargs):
    """
    Upload an image to Cloudinary.
    Returns dict with 'secure_url' and 'public_id'.
    """
    try:
        result = cloudinary.uploader.upload(
            file,
            folder=folder,
            format="webp",
            transformation={"quality": "auto", "fetch_format": "auto"},
            **kwargs,
        )
        return {
            "url": result["secure_url"],
            "public_id": result["public_id"],
        }
    except Exception as e:
        logger.error("Cloudinary upload failed: %s", e)
        raise


def delete_image(public_id):
    """Delete an image from Cloudinary by public_id."""
    if not public_id:
        return
    try:
        cloudinary.uploader.destroy(public_id)
        logger.info("Deleted Cloudinary image: %s", public_id)
    except Exception as e:
        logger.warning("Cloudinary delete failed for %s: %s", public_id, e)
