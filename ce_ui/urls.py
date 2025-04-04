from django.conf import settings
from django.urls import include, path, re_path
from django.views.generic import RedirectView

from . import views

app_name = "ce_ui"

urlprefix = None  # No url prefix, this plugin wants to register top-level routes

#
# Top-level routes
#
urlpatterns = [
    #
    # Main entry points and static apps
    #
    path("", views.HomeView.as_view(), name="home"),
    path(
        "termsandconditions/",
        views.TermsView.as_view(),
        name="terms",
    ),
    path(
        "search/",
        RedirectView.as_view(pattern_name="ce_ui:select"),
        name="search",
    ),
    #
    # Allauth
    #
    path("accounts/", include("allauth.urls")),
    #
    # For asking for terms and conditions
    #
    # some url specs are overwritten here pointing to own views in order to plug in
    # some extra context for the tabbed interface
    # View Specific Active Terms
    re_path(
        r"^terms/view/(?P<slug>[a-zA-Z0-9_.-]+)/$",
        views.TermsDetailView.as_view(),
        name="tc_view_specific_page",
    ),
    # View Specific Version of Terms
    re_path(
        r"^terms/view/(?P<slug>[a-zA-Z0-9_.-]+)/(?P<version>[0-9.]+)/$",
        views.TermsDetailView.as_view(),
        name="tc_view_specific_version_page",
    ),
    # Print Specific Version of Terms
    re_path(
        r"^terms/print/(?P<slug>[a-zA-Z0-9_.-]+)/(?P<version>[0-9.]+)/$",
        views.TermsDetailView.as_view(
            template_name="termsandconditions/tc_print_terms.html"
        ),
        name="tc_print_page",
    ),
    # Accept Terms
    re_path(r"^terms/accept/$", views.TermsAcceptView.as_view(), name="tc_accept_page"),
    # Accept Specific Terms
    re_path(
        r"^terms/accept/(?P<slug>[a-zA-Z0-9_.-]+)$",
        views.TermsAcceptView.as_view(),
        name="tc_accept_specific_page",
    ),
    # Accept Specific Terms Version
    re_path(
        r"^terms/accept/(?P<slug>[a-zA-Z0-9_.-]+)/(?P<version>[0-9\.]+)/$",
        views.TermsAcceptView.as_view(),
        name="tc_accept_specific_version_page",
    ),
    # the defaults
    re_path(r"^terms/", include("termsandconditions.urls")),
]

#
# Routes under the 'ui/' prefix
#
ui_urlpatterns = [
    #
    # User management
    #
    # path("", view=views.UserListView.as_view(), name="list"),
    path(
        "user-redirect/",
        view=views.UserRedirectView.as_view(),
        name="user-redirect",
    ),
    path("user-update/", view=views.UserUpdateView.as_view(), name="user-update"),
    path(
        "user/<str:username>/",
        view=views.UserDetailView.as_view(),
        name="user-detail",
    ),
    path(
        "user-email/", views.TabbedEmailView.as_view(), name="account_email"
    ),  # same as allauth.accounts.email.EmailView, but with tab data
    #
    # HTML routes
    #
    path("dataset-list/", view=views.DataSetListView.as_view(), name="select"),
    path(
        r"topography/<int:pk>/",
        view=views.TopographyDetailView.as_view(),
        name="topography-detail",
    ),
    path(
        r"dataset-detail/<int:pk>/",
        view=views.DatasetDetailView.as_view(),
        name="surface-detail",
    ),
    path(
        r"dataset-publish/<int:pk>/",
        view=views.DatasetPublishView.as_view(),
        name="dataset-publish",
    ),
    path(
        "analysis-list/",
        view=views.AnalysisListView.as_view(),
        name="results-list",
    ),
    path(
        r"analysis-detail/<str:slug>/",
        view=views.AnalysisDetailView.as_view(),
        name="results-detail",
    )
]
urlpatterns += [path("ui/", include((ui_urlpatterns, app_name)))]

#
# Challenge redirect
#
if settings.CHALLENGE_REDIRECT_URL:
    urlpatterns += [
        path(
            "challenge/",
            RedirectView.as_view(url=settings.CHALLENGE_REDIRECT_URL, permanent=False),
            name="challenge",
        ),
    ]
