import pytest
from allauth.socialaccount.models import SocialApp


@pytest.fixture
def orcid_socialapp(db):
    """Fixture for ORCID social app. Uses db fixture for database access."""
    social_app = SocialApp.objects.create(provider='orcid', name='ORCID')
    social_app.sites.set([1])
    return social_app


@pytest.fixture
def google_socialapp(db):
    """Fixture for the Google social app, the second identity provider."""
    social_app = SocialApp.objects.create(provider='google', name='Google')
    social_app.sites.set([1])
    return social_app
