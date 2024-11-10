import pytest
from django.shortcuts import reverse
from django.utils import timezone
from termsandconditions.models import TermsAndConditions
from topobank.testing.utils import assert_in_content, assert_not_in_content

#
# The code in this library relies on a middleware which replaces
# Django's AnonymousUser by our own anonymous user (that has a database id)
#


@pytest.mark.django_db
def test_anonymous_user_only_published_as_default(client, orcid_socialapp):
    response = client.get(reverse("ce_ui:select"))
    assert_not_in_content(response, "All accessible datasets")
    assert_not_in_content(response, "Unpublished datasets created by me")
    assert_not_in_content(response, "Unpublished datasets created by others")
    assert_in_content(response, "Published datasets")


@pytest.mark.django_db
def test_terms_conditions_as_anonymous(
    client, handle_usage_statistics, orcid_socialapp
):
    # Install terms and conditions for test
    TermsAndConditions.objects.create(
        slug="test-terms",
        name="Test of T&amp;C",
        text="some text",
        date_active=timezone.now(),
    )

    response = client.get(reverse("terms"))
    assert_in_content(response, "Test of T&amp;C")

    response = client.get(
        reverse("tc_accept_specific_page", kwargs=dict(slug="test-terms"))
    )
    assert_in_content(response, "some text")
