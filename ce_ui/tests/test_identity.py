"""Tests for connected identities and the ORCID requirement on publications."""

import pytest
from allauth.socialaccount.models import SocialAccount, SocialLogin
from django.contrib.auth import get_user_model
from django.core.exceptions import (ImproperlyConfigured, PermissionDenied,
                                    ValidationError)
from django.http import HttpResponse
from django.test import RequestFactory
from django.urls import path

from ce_ui.users.adapters import AccountAdapter, SocialAccountAdapter
from ce_ui.users.decorators import orcid_required, require_orcid_for_routes
from ce_ui.users.identity import (ORCID_REQUIRED_FOR_PUBLICATION, can_publish,
                                  connected_identities, has_orcid)


@pytest.fixture
def user(db):
    User = get_user_model()
    return User.objects.create_user(username="alice", password="password", name="Alice")


@pytest.fixture
def user_without_password(db):
    User = get_user_model()
    user = User.objects.create(username="bob", name="Bob")
    user.set_unusable_password()
    user.save()
    return user


def connect_orcid(user, uid="0000-0002-1825-0097"):
    return SocialAccount.objects.create(
        user=user,
        provider="orcid",
        uid=uid,
        extra_data={
            "orcid-identifier": {
                "uri": f"https://orcid.org/{uid}",
                "path": uid,
                "host": "orcid.org",
            }
        },
    )


def connect_google(user, uid="1234567890"):
    return SocialAccount.objects.create(
        user=user, provider="google", uid=uid, extra_data={"email": "alice@example.com"}
    )


#
# Which identities a user has
#


@pytest.mark.django_db
def test_user_without_social_account_has_no_orcid(user):
    assert not has_orcid(user)
    assert not user.has_orcid
    assert user.orcid_id is None


@pytest.mark.django_db
def test_google_account_is_not_an_orcid(user):
    connect_google(user)
    assert not user.has_orcid


@pytest.mark.django_db
def test_orcid_added_later_is_picked_up(user):
    assert not user.has_orcid
    connect_orcid(user)
    assert user.has_orcid
    assert user.orcid_id == "0000-0002-1825-0097"


@pytest.mark.django_db
def test_local_account_is_listed_as_an_identity(user):
    identities = connected_identities(user)
    assert [identity["provider"] for identity in identities] == ["local"]


@pytest.mark.django_db
def test_all_connected_identities_are_listed(user):
    connect_orcid(user)
    connect_google(user)
    identities = user.connected_identities
    assert {identity["provider"] for identity in identities} == {
        "orcid",
        "google",
        "local",
    }
    orcid = next(i for i in identities if i["provider"] == "orcid")
    assert orcid["name"] == "ORCID"
    assert orcid["url"] == "https://orcid.org/0000-0002-1825-0097"


@pytest.mark.django_db
def test_account_without_password_has_no_local_identity(user_without_password):
    connect_google(user_without_password)
    identities = connected_identities(user_without_password)
    assert [identity["provider"] for identity in identities] == ["google"]


def test_anonymous_user_has_no_identities():
    from django.contrib.auth.models import AnonymousUser

    assert connected_identities(AnonymousUser()) == []
    assert not has_orcid(AnonymousUser())


#
# Publishing requires an ORCID iD
#


@pytest.mark.django_db
def test_publishing_requires_an_orcid(user):
    assert not can_publish(user)
    connect_orcid(user)
    assert can_publish(user)


@pytest.mark.django_db
def test_view_without_orcid_is_refused(user):
    view = orcid_required(lambda request: HttpResponse("published"))
    request = RequestFactory().post("/go/publish/")
    request.user = user

    with pytest.raises(PermissionDenied) as exception:
        view(request)
    assert ORCID_REQUIRED_FOR_PUBLICATION in str(exception.value)


@pytest.mark.django_db
def test_view_with_orcid_is_allowed(user):
    connect_orcid(user)
    view = orcid_required(lambda request: HttpResponse("published"))
    request = RequestFactory().post("/go/publish/")
    request.user = user

    assert view(request).status_code == 200


#
# Guarding the publication routes of another plugin
#


def _view(request, **kwargs):
    return HttpResponse()


@pytest.mark.django_db
def test_only_the_named_routes_are_guarded(user):
    urlpatterns = [
        path("publish/", _view, name="publish"),
        path("<str:short_url>/", _view, name="go"),
    ]
    guarded = require_orcid_for_routes(urlpatterns, ["publish/"])

    request = RequestFactory().get("/go/anything/")
    request.user = user
    # The public landing page stays reachable without an ORCID iD ...
    assert guarded[1].callback(request, short_url="anything").status_code == 200
    # ... while publishing does not.
    with pytest.raises(PermissionDenied):
        guarded[0].callback(request)


def test_names_and_arguments_of_guarded_routes_are_kept():
    urlpatterns = [path("publish/", _view, name="publish")]
    guarded = require_orcid_for_routes(urlpatterns, ["publish/"])
    assert guarded[0].name == "publish"
    assert str(guarded[0].pattern) == "publish/"


def test_unknown_route_is_an_error():
    urlpatterns = [path("publish/", _view, name="publish")]
    with pytest.raises(ImproperlyConfigured):
        require_orcid_for_routes(urlpatterns, ["publish/", "renamed/"])


#
# Connecting and disconnecting accounts
#


@pytest.mark.django_db
def test_local_registration_follows_the_setting(settings, rf):
    # Off on this site, because a local registration would create an account
    # with no ORCID iD. See `test_signup_policy`.
    settings.ACCOUNT_ALLOW_SIGNUP = True
    assert AccountAdapter().is_open_for_signup(rf.get("/accounts/signup/"))
    settings.ACCOUNT_ALLOW_SIGNUP = False
    assert not AccountAdapter().is_open_for_signup(rf.get("/accounts/signup/"))


@pytest.mark.django_db
def test_closing_local_signup_leaves_orcid_open(settings, rf, user):
    """
    The two are separate switches. django-allauth's social adapter defers to
    the account adapter by default, which would close ORCID along with local
    registration; the override is what keeps them apart.
    """
    settings.ACCOUNT_ALLOW_SIGNUP = False
    assert not AccountAdapter().is_open_for_signup(rf.get("/accounts/signup/"))

    sociallogin = SocialLogin(
        user=user, account=SocialAccount(provider="orcid", uid="0000-0002-1825-0097")
    )
    assert SocialAccountAdapter().is_open_for_signup(rf.get("/"), sociallogin)


@pytest.mark.django_db
def test_last_sign_in_method_cannot_be_disconnected(user_without_password):
    google = connect_google(user_without_password)
    with pytest.raises(ValidationError):
        SocialAccountAdapter().validate_disconnect(google, [google])


@pytest.mark.django_db
def test_account_can_be_disconnected_when_another_remains(user_without_password):
    google = connect_google(user_without_password)
    orcid = connect_orcid(user_without_password)
    # No exception: the ORCID account is left to sign in with
    SocialAccountAdapter().validate_disconnect(google, [google, orcid])


@pytest.mark.django_db
def test_account_can_be_disconnected_when_a_password_remains(user):
    google = connect_google(user)
    SocialAccountAdapter().validate_disconnect(google, [google])


@pytest.mark.django_db
@pytest.mark.parametrize(
    "data",
    [
        {"first_name": "Ada", "last_name": "Lovelace"},
        {"name": "Ada Lovelace"},
    ],
)
def test_name_is_taken_from_the_provider(data):
    User = get_user_model()
    populated = SocialAccountAdapter().populate_user(
        None, SocialLogin(user=User()), data
    )
    assert populated.name == "Ada Lovelace"
