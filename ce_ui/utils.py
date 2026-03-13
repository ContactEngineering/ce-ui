from django.contrib.auth.models import Group

DEFAULT_GROUP_NAME = "all"


def get_default_group():
    group, created = Group.objects.get_or_create(name=DEFAULT_GROUP_NAME)
    return group

import logging
from django.conf import settings
from django.core.files.storage import default_storage
from django.core.exceptions import SuspiciousFileOperation
from django.urls import reverse

_log = logging.getLogger(__name__)

def get_upload_instructions(manifest, expire=3600, method=None):
    """Generate a presigned URL for an upload directly to S3"""
    # Preserve the trailing slash after normalizing the path.
    if method is None:
        method = settings.UPLOAD_METHOD

    if settings.USE_S3_STORAGE:
        # _normalize_name attaches the MEDIA_ROOT to the path. This is
        # typically done by default_storage.path, but S3 complains that
        # it does not support absolute paths if we use this method.
        try:
            storage_path = default_storage._normalize_name(
                manifest.generate_storage_path()
            )
        except SuspiciousFileOperation:
            # This happens after migrations, when the file name is not yet set
            _log.info(
                f"Manifest {manifest.id} has no file associated with it, and the "
                f"filename '{manifest.filename}' appears invalid. Cannot generate "
                "upload instructions."
            )
            return {}
        if method == "POST":
            upload_instructions = (
                default_storage.bucket.meta.client.generate_presigned_post(
                    Bucket=settings.AWS_STORAGE_BUCKET_NAME,
                    Key=storage_path,
                    ExpiresIn=expire,
                )
            )
            upload_instructions["method"] = "POST"
        elif method == "PUT":
            upload_instructions = {
                "method": "PUT",
                "url": default_storage.bucket.meta.client.generate_presigned_url(
                    ClientMethod="put_object",
                    Params={
                        "Bucket": settings.AWS_STORAGE_BUCKET_NAME,
                        "Key": storage_path,
                        # ContentType must match content type of put request
                        "ContentType": "binary/octet-stream",
                    },
                    ExpiresIn=expire,
                ),
            }
        else:
            raise RuntimeError(f"Unknown upload method: {method}")
    else:
        if method != "POST":
            raise RuntimeError("Only POST uploads are supported without S3")
        upload_instructions = {
            "method": "POST",
            "url": reverse(
                "files:upload-direct-local", kwargs=dict(manifest_id=manifest.id)
            ),
            "fields": {},
        }
    return upload_instructions
