from django.urls import re_path, path

from . import views

app_name = "ui"
urlprefix='ui/'
urlpatterns = [
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
