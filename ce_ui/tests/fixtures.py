import pytest
from allauth.socialaccount.models import SocialApp


@pytest.fixture
def orcid_socialapp(db):
    """Fixture for ORCID social app. Uses db fixture for database access."""
    social_app = SocialApp.objects.create(provider='orcid', name='ORCID')
    social_app.sites.set([1])
    return social_app
