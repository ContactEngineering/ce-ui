import notifications.urls
from django.conf import settings
from django.contrib import admin
from django.contrib.auth.decorators import user_passes_test
from django.contrib.auth.views import login_required
from django.contrib.staticfiles import views as static_views
from django.urls import include, path, re_path
from django.views import defaults as default_views
from django.views.generic import RedirectView
from drf_spectacular.views import SpectacularAPIView, SpectacularSwaggerView

from topobank.organizations.models import Organization
from topobank_rest_api.views import entry_points

from . import views

# Plugin URLs
import topobank_contact.urls
import topobank_publication.urls
import topobank_statistics.urls

app_name = "ce_ui"


def plugin_urls(urllist, app_label, restricted):
    for entry in urllist:
        if hasattr(entry, "url_patterns"):
            # This is a list of URL patterns
            entry.url_patterns = plugin_urls(entry.url_patterns, app_label, restricted)
        elif hasattr(entry, "callback"):
            # This is a path with a view
            def plugin_available_check(user):
                if restricted:
                    return app_label in Organization.objects.get_plugins_available(user)
                return True

            callback_decorator = user_passes_test(
                plugin_available_check, login_url="/403/", redirect_field_name=None
            )
            entry.callback = callback_decorator(entry.callback)
    return urllist


#
# Plugin URL patterns
#
plugin_patterns = [
    path(
        topobank_contact.urls.urlprefix,
        include((plugin_urls(topobank_contact.urls.urlpatterns, "topobank_contact", True), "topobank_contact")),
    ),
    path(
        topobank_publication.urls.urlprefix,
        include((plugin_urls(topobank_publication.urls.urlpatterns, "topobank_publication", False), "topobank_publication")),
    ),
    path(
        topobank_statistics.urls.urlprefix,
        include((plugin_urls(topobank_statistics.urls.urlpatterns, "topobank_statistics", False), "topobank_statistics")),
    ),
]

#
# Top-level routes
#
urlpatterns = plugin_patterns + [
    #
    # Entry points
    #
    path("entry-points/", entry_points),
    #
    # Main entry points and static apps
    #
    path("", views.HomeView.as_view(), name="home"),
    path(
        "termsandconditions/",
        views.TermsListView.as_view(),
        name="terms",
    ),
    path(
        "search/",
        RedirectView.as_view(pattern_name="ce_ui:select"),
        name="search",
    ),
    #
    # Core topobank applications
    #
    path(
        "",
        include(
            [
                path(
                    "users/",
                    include("topobank_rest_api.users.urls", namespace="users"),
                ),
                path(
                    "organizations/",
                    include("topobank_rest_api.organizations.urls", namespace="organizations"),
                ),
                path(
                    "authorization/",
                    include("topobank_rest_api.authorization.urls", namespace="authorization"),
                ),
                path(
                    "files/",
                    include("topobank_rest_api.files.urls", namespace="files"),
                ),
                path(
                    "manager/",
                    include("topobank_rest_api.manager.urls", namespace="manager"),
                ),
                path(
                    "analysis/",
                    include("topobank_rest_api.analysis.urls", namespace="analysis"),
                ),
            ]
        ),
    ),
    path(
        "plugins/",
        include(
            [
                path(
                    topobank_contact.urls.urlprefix,
                    include((plugin_urls(topobank_contact.urls.urlpatterns, "topobank_contact", True), "topobank_contact")),
                ),
                path(
                    topobank_publication.urls.urlprefix,
                    include((plugin_urls(topobank_publication.urls.urlpatterns, "topobank_publication", False), "publication")),
                ),
                path(
                    topobank_statistics.urls.urlprefix,
                    include((plugin_urls(topobank_statistics.urls.urlpatterns, "topobank_statistics", False), "topobank_statistics")),
                ),
            ]
        ),
    ),
    #
    # Allauth
    #
    path("accounts/", include("allauth.urls")),
    #
    # Django Admin, use {% url 'admin:index' %}
    #
    path(settings.ADMIN_URL, admin.site.urls),
    #
    # Notifications - see package django-notifications
    # Note: plugin's may provided optimized wrapper views that take precedence
    #
    re_path(
        "^inbox/notifications/", include(notifications.urls, namespace="notifications")
    ),
    #
    # Watchman - see package django-watchman
    # Note: plugin's may provided optimized wrapper views that take precedence
    #
    path("watchman/", include(("watchman.urls", "watchman"), namespace="watchman")),
    #
    # Open API
    #
    path("api/schema/", SpectacularAPIView.as_view(), name="schema"),
    path(
        "api/schema/swagger-ui/",
        SpectacularSwaggerView.as_view(url_name="schema"),
        name="swagger-ui",
    ),
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
        "dataset-collection-list/",
        view=views.DatasetCollectionListView.as_view(),
        name="collections",
    ),
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
        r"dataset-collection-publish/",
        view=login_required(views.DatasetCollectionPublishView.as_view()),
        name="dataset-collection-publish",
    ),
    path(
        r"dataset-collection/<int:pk>/",
        view=views.DatasetCollectionView.as_view(),
        name="dataset-collection",
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
    ),
]
urlpatterns += [path("ui/", include((ui_urlpatterns, app_name)))]

#
# Routes under the 'challenge/' prefix
#
challenge_urlpatterns = [
    #
    # User management
    #
    path(
        r"",
        view=views.ChallengeHomepageView.as_view(),
        name="homepage",
    ),
    path(
        r"list-of-published-data/",
        view=views.ChallengeListOfPublishedDataView.as_view(),
        name="list-of-published-data",
    ),
]

urlpatterns += [
    path(
        "challenge/",
        include((challenge_urlpatterns, "challenge"), namespace="challenge"),
    )
]

if settings.DEBUG:
    # This allows the error pages to be debugged during development, just visit
    # these url in browser to see how these error pages look like.
    urlpatterns += [
        path(
            "400/",
            default_views.bad_request,
            kwargs={"exception": Exception("Bad Request!")},
        ),
        path(
            "403/",
            default_views.permission_denied,
            kwargs={"exception": Exception("Permission Denied")},
        ),
        path(
            "404/",
            default_views.page_not_found,
            kwargs={"exception": Exception("Page not Found")},
        ),
        path("500/", default_views.server_error),
        re_path(r"^static/(?P<path>.*)$", static_views.serve),
    ]
    if "debug_toolbar" in settings.INSTALLED_APPS:
        import debug_toolbar

        urlpatterns = [path("__debug__/", include(debug_toolbar.urls))] + urlpatterns
