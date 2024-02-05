import pytest

from allauth.socialaccount.models import SocialApp


@pytest.mark.django_db
@pytest.fixture
def orcid_socialapp():
    social_app = SocialApp.objects.create(provider='orcid', name='ORCID')
    social_app.sites.set([1])
