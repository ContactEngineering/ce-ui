from django.conf import settings
from django.urls import include, re_path, path
from django.views.generic import TemplateView, RedirectView

from . import views

app_name = "ce_ui"

urlprefix = None  # No url prefix, this plugin wants to register top-level routes

#
# Top-level routes
#
urlpatterns = [
    #
    # Main entry points and static pages
    #
    path("", views.HomeView.as_view(), name="home"),
    path(
        "about/",
        TemplateView.as_view(template_name="pages/about.html"),
        name="about",
    ),
    path(
        "termsandconditions/",
        views.TermsView.as_view(),
        name="terms",
    ),
    path(
        "help/",
        views.HelpView.as_view(),
        name="help",
    ),
    path(
        "search/",
        RedirectView.as_view(pattern_name='ce_ui:select'),
        name="search",
    ),
    #
    # For asking for terms and conditions
    #
    # some url specs are overwritten here pointing to own views in order to plug in
    # some extra context for the tabbed interface
    # View Specific Active Terms
    re_path(r'^terms/view/(?P<slug>[a-zA-Z0-9_.-]+)/$', views.TermsDetailView.as_view(),
            name="tc_view_specific_page"),

    # View Specific Version of Terms
    re_path(r'^terms/view/(?P<slug>[a-zA-Z0-9_.-]+)/(?P<version>[0-9.]+)/$', views.TermsDetailView.as_view(),
            name="tc_view_specific_version_page"),

    # Print Specific Version of Terms
    re_path(r'^terms/print/(?P<slug>[a-zA-Z0-9_.-]+)/(?P<version>[0-9.]+)/$',
            views.TermsDetailView.as_view(template_name="termsandconditions/tc_print_terms.html"),
            name="tc_print_page"),

    # Accept Terms
    re_path(r'^terms/accept/$', views.TermsAcceptView.as_view(), name="tc_accept_page"),

    # Accept Specific Terms
    re_path(r'^terms/accept/(?P<slug>[a-zA-Z0-9_.-]+)$', views.TermsAcceptView.as_view(),
            name="tc_accept_specific_page"),

    # Accept Specific Terms Version
    re_path(r'^terms/accept/(?P<slug>[a-zA-Z0-9_.-]+)/(?P<version>[0-9\.]+)/$', views.TermsAcceptView.as_view(),
            name="tc_accept_specific_version_page"),

    # the defaults
    re_path(r'^terms/', include('termsandconditions.urls')),
]

#
# Routes under the 'ui/' prefix
#
ui_urlpatterns = [
    #
    # HTML routes
    #
    path(
        'html/dataset-list/',
        view=views.DataSetListView.as_view(),
        name='select'
    ),
    path(
        r'html/topography/',
        view=views.TopographyDetailView.as_view(),
        name='topography-detail'
    ),
    path(
        r'html/surface/',
        view=views.SurfaceDetailView.as_view(),
        name='surface-detail'
    ),
    path(
        'html/analysis-list/',
        view=views.AnalysesResultListView.as_view(),
        name='results-list'
    ),
    path(
        r'html/analysis-detail/<int:pk>/',
        view=views.AnalysisResultDetailView.as_view(),
        name='results-detail'
    ),
    #
    # Data routes
    #
    path(
        'select/download/',
        view=views.download_selection_as_surfaces,
        name='download-selection'
    ),
    #
    # API routes
    #
    path(
        'api/search/',  # TODO check URL, rename?
        view=views.SurfaceListView.as_view(),  # TODO Check view name, rename?
        name='search'  # TODO rename?
    ),
    path(
        'api/tag-tree/',
        view=views.TagTreeView.as_view(),
        name='tag-list'  # TODO rename
    ),
    re_path(
        r'api/selection/surface/(?P<pk>\d+)/select/$',
        view=views.select_surface,
        name='surface-select'
    ),
    re_path(
        r'api/selection/surface/(?P<pk>\d+)/unselect/$',
        view=views.unselect_surface,
        name='surface-unselect'
    ),
    re_path(
        r'api/selection/topography/(?P<pk>\d+)/select/$',
        view=views.select_topography,
        name='topography-select'
    ),
    re_path(
        r'api/selection/topography/(?P<pk>\d+)/unselect/$',
        view=views.unselect_topography,
        name='topography-unselect'
    ),
    re_path(
        r'api/selection/tag/(?P<pk>\d+)/select/$',
        view=views.select_tag,
        name='tag-select'
    ),
    re_path(
        r'api/selection/tag/(?P<pk>\d+)/unselect/$',
        view=views.unselect_tag,
        name='tag-unselect'
    ),
    path(
        'api/selection/unselect-all/',
        view=views.unselect_all,
        name='unselect-all'
    )
]
urlpatterns += [path('ui/', include((ui_urlpatterns, app_name)))]

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
