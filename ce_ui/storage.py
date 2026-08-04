"""Storage backends."""

from django.core.cache import cache
from storages.backends.s3boto3 import S3Boto3Storage


class CachedPresignedUrlStorage(S3Boto3Storage):
    """S3 storage that memoizes presigned URLs.

    Signing is cheap, but a fresh signature per response means the URL for the
    same object differs between page loads, so browsers can never serve it
    from their cache and re-download thumbnails, plot data and deep-zoom tiles
    on every visit. Handing out the same signed URL for half its lifetime lets
    repeat requests hit the browser cache instead of the object store.

    Files in the data lake are immutable — replacing a file means creating a
    new manifest under a new storage path — so a memoized URL can never point
    at stale content. Note that a signed URL stays valid for its full lifetime
    regardless of later permission changes; memoization does not change that,
    it only means the window is used rather than wasted.
    """

    def url(self, name, parameters=None, expire=None, http_method=None):
        if parameters or expire or http_method:
            # Requests with special parameters are signed fresh
            return super().url(
                name, parameters=parameters, expire=expire, http_method=http_method
            )
        if not self.querystring_auth:
            # Unsigned URLs are stable already
            return super().url(name)
        cache_key = f"presigned-url:{self.location}:{name}"
        url = cache.get(cache_key)
        if url is None:
            url = super().url(name)
            # Serve the same URL for half its lifetime, so that a URL handed
            # out at the end of the memoization window is still valid for at
            # least the other half.
            cache.set(cache_key, url, timeout=max(self.querystring_expire // 2, 60))
        return url
