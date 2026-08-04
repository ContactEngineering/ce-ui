"""Tests for the presigned-URL memoizing storage backend.

The point of `CachedPresignedUrlStorage` is that the URL for one stored object
does not change on every request, because a URL that changes can never be
served from the browser cache. These tests therefore check what the *caller*
observes -- the same URL string, produced by a single signature -- rather than
the internals of the cache.

No S3 is involved: the parent's signing method is replaced by one that returns a
different URL every time it is called, so a repeated signature is detectable.
"""

import pytest
from storages.backends.s3boto3 import S3Boto3Storage

from ce_ui.storage import CachedPresignedUrlStorage

#: A day, matching the `AWS_QUERYSTRING_EXPIRE` default.
ONE_DAY = 86400


class RecordingCache:
    """Stands in for the Django cache, keeping the timeouts it was given."""

    def __init__(self):
        self.values = {}
        self.timeouts = {}

    def get(self, key):
        return self.values.get(key)

    def set(self, key, value, timeout=None):
        self.values[key] = value
        self.timeouts[key] = timeout


@pytest.fixture
def signatures(monkeypatch):
    """Replace the parent's signing with a counter, and report the calls."""
    calls = []

    def fake_url(self, name, parameters=None, expire=None, http_method=None):
        calls.append(
            {
                "name": name,
                "parameters": parameters,
                "expire": expire,
                "http_method": http_method,
            }
        )
        # A real presigned URL differs on every signature; so does this one.
        return f"https://s3.invalid/{name}?signature={len(calls)}"

    monkeypatch.setattr(S3Boto3Storage, "url", fake_url)
    return calls


@pytest.fixture
def cache(monkeypatch):
    recording = RecordingCache()
    monkeypatch.setattr("ce_ui.storage.cache", recording)
    return recording


def make_storage(location="media", querystring_expire=ONE_DAY, querystring_auth=True):
    """A storage instance configured without touching S3 or the settings.

    Only `url()` is under test and it reads exactly these three attributes, so
    the instance is built without running the boto3-backed constructor.
    """
    storage = CachedPresignedUrlStorage.__new__(CachedPresignedUrlStorage)
    storage.location = location
    storage.querystring_expire = querystring_expire
    storage.querystring_auth = querystring_auth
    return storage


def test_the_same_object_keeps_the_same_url(signatures, cache):
    storage = make_storage()

    first = storage.url("thumbnails/1.png")
    second = storage.url("thumbnails/1.png")

    # One signature, handed out twice: this is what lets a browser reuse what it
    # already downloaded.
    assert first == second
    assert len(signatures) == 1


def test_each_object_gets_its_own_url(signatures, cache):
    storage = make_storage()

    first = storage.url("thumbnails/1.png")
    second = storage.url("thumbnails/2.png")

    assert first != second
    assert len(signatures) == 2
    # ...and the first one is still served from the cache afterwards
    assert storage.url("thumbnails/1.png") == first
    assert len(signatures) == 2


def test_url_is_cached_for_half_its_lifetime(signatures, cache):
    storage = make_storage(querystring_expire=ONE_DAY)

    storage.url("thumbnails/1.png")

    (timeout,) = cache.timeouts.values()
    # Half, so that a URL handed out at the end of the window is still valid for
    # at least the other half of its lifetime.
    assert timeout == ONE_DAY // 2


def test_very_short_lived_urls_are_still_cached_briefly(signatures, cache):
    storage = make_storage(querystring_expire=10)

    storage.url("thumbnails/1.png")

    (timeout,) = cache.timeouts.values()
    # A floor keeps the cache useful when the signature lifetime is tiny; the
    # URL may then outlive its own validity, which is why the floor is low.
    assert timeout == 60


@pytest.mark.parametrize(
    "kwargs",
    [
        {"parameters": {"ResponseContentDisposition": "attachment"}},
        {"expire": 30},
        {"http_method": "PUT"},
    ],
    ids=["parameters", "expire", "http_method"],
)
def test_requests_asking_for_something_special_are_signed_fresh(
    signatures, cache, kwargs
):
    storage = make_storage()

    storage.url("thumbnails/1.png", **kwargs)
    storage.url("thumbnails/1.png", **kwargs)

    # A download-with-filename or an upload URL is not the plain object URL, so
    # it must neither be served from nor written to the cache.
    assert len(signatures) == 2
    assert cache.values == {}
    # The request is forwarded unchanged
    for key, value in kwargs.items():
        assert signatures[0][key] == value


def test_a_special_request_does_not_evict_the_plain_url(signatures, cache):
    storage = make_storage()
    plain = storage.url("thumbnails/1.png")

    storage.url("thumbnails/1.png", parameters={"ResponseContentType": "image/png"})

    assert storage.url("thumbnails/1.png") == plain


def test_public_buckets_are_left_alone(signatures, cache):
    storage = make_storage(querystring_auth=False)

    storage.url("thumbnails/1.png")
    storage.url("thumbnails/1.png")

    # An unsigned URL is already stable, so there is nothing to memoize
    assert cache.values == {}
    assert len(signatures) == 2


def test_two_prefixes_do_not_share_a_url(signatures, cache):
    media = make_storage(location="media")
    other = make_storage(location="other")

    from_media = media.url("thumbnails/1.png")
    from_other = other.url("thumbnails/1.png")

    # Same name under a different prefix is a different object; if the cache key
    # ignored the prefix, one would be served the other's URL.
    assert from_media != from_other
    assert len(signatures) == 2
