import pytest
from django.shortcuts import reverse
from django.utils import timezone

from topobank.utils import assert_in_content, assert_not_in_content
from termsandconditions.models import TermsAndConditions


#
# The code in these tests rely on a middleware which replaces
# Django's AnonymousUser by the one of django guardian
#


@pytest.mark.django_db
def test_anonymous_user_only_published_as_default(client):
    response = client.get(reverse('ce_ui:select'))
    assert_not_in_content(response, 'All accessible surfaces')
    assert_not_in_content(response, 'Only own surfaces')
    assert_not_in_content(response, 'Only surfaces shared with you')
    assert_not_in_content(response, 'Only surfaces shared by you')
    assert_not_in_content(response, 'Only surfaces published by you')
    assert_in_content(response, 'Only surfaces published by others')


@pytest.mark.django_db
def test_terms_conditions_as_anonymous(client):
    # Install terms and conditions for test
    TermsAndConditions.objects.create(slug='test-terms', name="Test of T&amp;C",
                                      text="some text", date_active=timezone.now())

    response = client.get(reverse('terms'))
    assert_in_content(response, "Test of T&amp;C")

    response = client.get(reverse('tc_accept_specific_page', kwargs=dict(slug='test-terms')))
    assert_in_content(response, "some text")
