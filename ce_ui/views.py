import logging
from html import unescape
from io import BytesIO

from allauth.account.views import EmailView
from django.contrib.auth import get_user_model
from django.contrib.auth.mixins import LoginRequiredMixin
from django.core.exceptions import PermissionDenied
from django.db.models import Q, Subquery, TextField, Value
from django.db.models.functions import Replace
from django.http import HttpResponse
from django.urls import reverse
from django.views.generic import (DetailView, ListView, RedirectView,
                                  TemplateView, UpdateView)
from rest_framework import generics
from rest_framework.decorators import api_view, permission_classes
from rest_framework.pagination import PageNumberPagination
from rest_framework.response import Response
from rest_framework.utils.urls import remove_query_param, replace_query_param
from termsandconditions.models import TermsAndConditions
from termsandconditions.views import AcceptTermsView
from termsandconditions.views import TermsView as OrigTermsView
from topobank.analysis.models import AnalysisFunction
from topobank.analysis.registry import (get_analysis_function_names,
                                        get_visualization_type)
from topobank.manager.containers import write_surface_container
from topobank.manager.models import Surface, Tag, Topography
from topobank.manager.utils import subjects_from_base64
from topobank.usage_stats.utils import (current_statistics,
                                        increase_statistics_by_date,
                                        increase_statistics_by_date_and_object)
from topobank.users.models import User
from trackstats.models import Metric, Period

from ce_ui import breadcrumb

from .serializers import SurfaceSearchSerializer, TagSearchSerizalizer
from .utils import (current_selection_as_basket_items,
                    filter_queryset_by_search_term, filtered_topographies,
                    get_order_by, get_search_term, get_sharing_status,
                    get_tree_mode, instances_to_selection, selected_instances,
                    selection_to_subjects_dict, tags_for_user)

ORDER_BY_CHOICES = {"name": "name", "-creation_datetime": "date"}
SHARING_STATUS_FILTER_CHOICES = {
    "all": "All accessible datasets",
    "own": "Unpublished datasets created by me",
    "others": "Unpublished datasets created by others",
    "published": "Published datasets",
}
TREE_MODE_CHOICES = ["surface list", "tag tree"]

MAX_PAGE_SIZE = 100
DEFAULT_PAGE_SIZE = 10

DEFAULT_SELECT_TAB_STATE = {
    "search_term": "",  # empty string means: no search
    "order_by": "-creation_datetime",
    "sharing_status": "all",
    "tree_mode": "surface list",
    "page_size": 10,
    "current_page": 1,
    # all these values are the default if no filter has been applied
    # and the page is loaded the first time
}

DEFAULT_CONTAINER_FILENAME = "digital_surface_twin.zip"

_log = logging.getLogger(__name__)


def filtered_surfaces(request):
    """Return queryset with surfaces matching all filter criteria.

    Surfaces should be
    - readable by the current user
    - filtered by sharing status
    - filtered by search expression, if given

    Parameters
    ----------
    request
        Request instance

    Returns
    -------
        Filtered queryset of surfaces
    """

    user = request.user
    # start with all surfaces which are visible for the user
    qs = Surface.objects.for_user(user)

    #
    # Filter by sharing status
    #
    sharing_status = get_sharing_status(request)
    if sharing_status == "own":
        qs = qs.filter(creator=user)
        if hasattr(Surface, "publication"):
            qs = qs.exclude(
                publication__isnull=False
            )  # exclude published and own surfaces
    elif sharing_status == "others":
        qs = qs.exclude(creator=user)
        if hasattr(Surface, "publication"):
            qs = qs.exclude(
                publication__isnull=False
            )  # exclude published and own surfaces
    elif sharing_status == "published":
        if hasattr(Surface, "publication"):
            qs = qs.filter(publication__isnull=False)
        else:
            qs = Surface.objects.none()
    elif sharing_status == "all":
        pass
    else:
        raise ValueError(f"Unknown sharing status '{sharing_status}'.")

    #
    # Filter by search term
    #
    search_term = get_search_term(request)
    if search_term:
        #
        # search specific fields of all surfaces in a 'websearch' manner:
        # combine phrases by "AND", allow expressions and quotes
        #
        # See https://docs.djangoproject.com/en/3.2/ref/contrib/postgres/search/#full-text-search
        # for details.
        #
        # We introduce an extra field for search in tag names where the tag names
        # are changed so that the tokenizer splits the names into multiple words
        qs = (
            qs.annotate(
                tag_names_for_search=Replace(
                    Replace(
                        "tags__name", Value("."), Value(" ")
                    ),  # replace . with space
                    Value("/"),
                    Value(" "),
                ),  # replace / with space
                topography_tag_names_for_search=Replace(  # same for the topographies
                    Replace("topography__tags__name", Value("."), Value(" ")),
                    Value("/"),
                    Value(" "),
                ),
                topography_name_for_search=Replace(
                    "topography__name", Value("."), Value(" "), output_field=TextField()
                ),
                # often there are filenames
            )
            .distinct("id")
            .order_by("id")
        )
        qs = filter_queryset_by_search_term(
            qs,
            search_term,
            [
                "description",
                "name",
                "creator__name",
                "tag_names_for_search",
                "topography_name_for_search",
                "topography__description",
                "topography_tag_names_for_search",
                "topography__creator__name",
            ],
        )

    #
    # Sort results
    #
    order_by = get_order_by(request)
    qs = Surface.objects.filter(pk__in=Subquery(qs.values("pk"))).order_by(order_by)

    return qs


def download_selection_as_surfaces(request):
    """Returns a file comprised from surfaces related to the selection.

    :param request: current request
    :return:
    """

    from .utils import current_selection_as_surface_list

    surfaces = current_selection_as_surface_list(request)

    container_bytes = BytesIO()
    write_surface_container(container_bytes, surfaces)

    # Prepare response object.
    response = HttpResponse(
        container_bytes.getvalue(), content_type="application/x-zip-compressed"
    )
    response["Content-Disposition"] = 'attachment; filename="{}"'.format(
        DEFAULT_CONTAINER_FILENAME
    )
    # Since the selection contains multiple surfaces in general, we should think about
    # another file name in this case.

    # increase download count for each surface
    for surf in surfaces:
        increase_statistics_by_date_and_object(
            Metric.objects.SURFACE_DOWNLOAD_COUNT, period=Period.DAY, obj=surf
        )

    return response


class TopographyDetailView(TemplateView):
    template_name = "manager/topography_detail.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        #
        # Get surface instance
        #
        topography_id = self.request.GET.get("topography")
        if topography_id is None:
            return context
        try:
            topography = Topography.objects.get(id=int(topography_id))
        except (ValueError, Topography.DoesNotExist):
            raise PermissionDenied()

        #
        # Check permissions
        #
        if not topography.has_permission(self.request.user, "view"):
            raise PermissionDenied()

        #
        # Breadcrumb navigation
        #
        breadcrumb.add_surface(context, topography.surface)
        breadcrumb.add_topography(context, topography)

        return context


class DataSetListView(TemplateView):
    template_name = "manager/select.html"

    def dispatch(self, request, *args, **kwargs):
        # count this view event for statistics
        metric = Metric.objects.SEARCH_VIEW_COUNT
        increase_statistics_by_date(metric, period=Period.DAY)
        return super().dispatch(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        session = self.request.session

        search_term = get_search_term(self.request)
        if search_term:
            # When searching, we want the default select tab state except for
            # the search term, which is taken from thr request parameters.
            # If not using the default select tab state, this can result
            # in "Load Error!" on the page (#543) because e.g. page 2
            # is not available in the result.
            select_tab_state = DEFAULT_SELECT_TAB_STATE.copy()
            select_tab_state["search_term"] = search_term
        else:
            # .. otherwise keep search term from session variable 'select_tab_state'
            #    and all other state settings
            select_tab_state = session.get(
                "select_tab_state", default=DEFAULT_SELECT_TAB_STATE.copy()
            )

        # key: tree mode
        context["base_urls"] = {
            "surface list": self.request.build_absolute_uri(reverse("ce_ui:search")),
            "tag tree": self.request.build_absolute_uri(reverse("ce_ui:tag-list")),
        }

        context["order_by_filter_choices"] = ORDER_BY_CHOICES.copy()

        if self.request.user.is_anonymous:
            # Anonymous user have only one choice
            context["sharing_status_filter_choices"] = {
                "published": SHARING_STATUS_FILTER_CHOICES["published"]
            }
            select_tab_state["sharing_status"] = (
                "published"  # this only choice should be selected
            )
        else:
            context["sharing_status_filter_choices"] = (
                SHARING_STATUS_FILTER_CHOICES.copy()
            )

        context["select_tab_state"] = select_tab_state.copy()

        # The session needs a default for the state of the select tab
        session["select_tab_state"] = select_tab_state

        return context


class SurfaceDetailView(TemplateView):
    template_name = "manager/surface_detail.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        #
        # Get surface instance
        #
        surface_id = self.request.GET.get("surface")
        if surface_id is None:
            return context
        try:
            surface = Surface.objects.get(id=int(surface_id))
        except (ValueError, Surface.DoesNotExist):
            raise PermissionDenied()

        #
        # Check permissions
        #
        if not surface.has_permission(self.request.user, "view"):
            raise PermissionDenied()

        #
        # Breadcrumb navigation
        #
        breadcrumb.add_surface(context, surface)

        return context


#######################################################################################
# Views for REST interface
#######################################################################################
class SurfaceSearchPaginator(PageNumberPagination):
    page_size = DEFAULT_PAGE_SIZE
    page_query_param = "page"
    page_size_query_param = "page_size"
    max_page_size = MAX_PAGE_SIZE

    def get_paginated_response(self, data):

        #
        # Save information about requested data in session
        #
        session = self.request.session

        select_tab_state = session.get(
            "select_tab_state", DEFAULT_SELECT_TAB_STATE.copy()
        )
        # not using the keyword argument "default" here, because in some tests,
        # the session is a simple dict and no real session dict. A simple
        # dict's .get() has no keyword argument 'default', although it can be given
        # as second parameter.

        select_tab_state["search_term"] = get_search_term(self.request)
        select_tab_state["order_by"] = get_order_by(self.request)
        select_tab_state["sharing_status"] = get_sharing_status(self.request)
        select_tab_state["tree_mode"] = get_tree_mode(self.request)
        page_size = self.get_page_size(self.request)
        select_tab_state[self.page_size_query_param] = page_size
        select_tab_state["current_page"] = self.page.number
        _log.debug("Setting select tab state set in paginator: %s", select_tab_state)
        session["select_tab_state"] = select_tab_state

        return Response(
            {
                "num_items": self.page.paginator.count,
                "num_pages": self.page.paginator.num_pages,
                "page_range": list(self.page.paginator.page_range),
                "page_urls": list(self.get_page_urls()),
                "current_page": self.page.number,
                "num_items_on_current_page": len(self.page.object_list),
                "page_size": page_size,
                "search_term": select_tab_state["search_term"],
                "order_by": select_tab_state["order_by"],
                "sharing_status": select_tab_state["sharing_status"],
                "tree_mode": select_tab_state["tree_mode"],
                "page_results": data,
            }
        )

    def get_page_urls(self):
        base_url = self.request.build_absolute_uri()
        urls = []
        for page_no in self.page.paginator.page_range:
            if page_no == 1:
                url = remove_query_param(base_url, self.page_query_param)
            else:
                url = replace_query_param(base_url, self.page_query_param, page_no)
            # always add page size, so requests for other pages have it
            url = replace_query_param(
                url, self.page_size_query_param, self.get_page_size(self.request)
            )
            urls.append(url)
        return urls


class TagTreeView(generics.ListAPIView):
    """
    Generate tree of tags with surfaces and topographies underneath.
    """

    serializer_class = TagSearchSerizalizer
    pagination_class = SurfaceSearchPaginator

    def get_queryset(self):
        surfaces = filtered_surfaces(self.request)
        topographies = filtered_topographies(self.request, surfaces)
        return tags_for_user(self.request.user, surfaces, topographies).filter(
            parent=None
        )
        # Only top level are collected, the children are added in the serializer.
        #
        # TODO The filtered surfaces and topographies are calculated twice here, not sure how to circumvent this.
        # Maybe by caching with request argument?

    def get_serializer_context(self):
        context = super().get_serializer_context()
        context["selected_instances"] = selected_instances(self.request)
        context["request"] = self.request

        surfaces = filtered_surfaces(self.request)
        topographies = filtered_topographies(self.request, surfaces)
        tags = tags_for_user(self.request.user, surfaces, topographies)
        context["tags_for_user"] = tags

        #
        # also pass filtered surfaces and topographies the user has access to
        #
        context["surfaces"] = surfaces
        context["topographies"] = topographies

        return context


# FIXME!!! This should be folded into the `SurfaceViewSet`, but handling
#  selections should be moved to the client first.
class SurfaceListView(generics.ListAPIView):
    """
    List all surfaces with topographies underneath.
    """

    serializer_class = SurfaceSearchSerializer
    pagination_class = SurfaceSearchPaginator

    def get_queryset(self):
        return filtered_surfaces(self.request)

    def get_serializer_context(self):
        context = super().get_serializer_context()
        context["selected_instances"] = selected_instances(self.request)
        context["request"] = self.request
        return context


def _selection_set(request):
    return set(request.session.get("selection", []))


def _surface_key(
    pk,
):  # TODO use such a function everywhere: instance_key_for_selection()
    return "surface-{}".format(pk)


def _topography_key(pk):
    return "topography-{}".format(pk)


def _tag_key(pk):
    return "tag-{}".format(pk)


def set_surface_select_status(request, pk, select_status):
    """Marks the given surface as 'selected' in session or checks this.

    :param request: request
    :param pk: primary key of the surface
    :param select_status: True if surface should be selected, False if it should be unselected
    :return: JSON Response

    The response returns the current selection as suitable for the basket.
    """
    try:
        pk = int(pk)
        surface = Surface.objects.get(pk=pk)
        assert surface.has_permission(request.user, "view")
    except (ValueError, Surface.DoesNotExist, AssertionError):
        raise PermissionDenied()  # This should be shown independent of whether the surface exists

    surface_key = _surface_key(pk)
    selection = _selection_set(request)
    is_selected = surface_key in selection

    if request.method == "POST":
        if select_status:
            # surface should be selected
            selection.add(surface_key)
        elif is_selected:
            selection.remove(surface_key)

        request.session["selection"] = list(selection)

    data = current_selection_as_basket_items(request)
    return Response(data)


@api_view(["POST"])
@permission_classes(
    []
)  # We need to override permissions because the anonymous user has read-only access
def select_surface(request, pk):
    """Marks the given surface as 'selected' in session.

    :param request: request
    :param pk: primary key of the surface
    :return: JSON Response

    The response returns the current selection as suitable for the basket.
    """
    return set_surface_select_status(request, pk, True)


@api_view(["POST"])
@permission_classes(
    []
)  # We need to override permissions because the anonymous user has read-only access
def unselect_surface(request, pk):
    """Marks the given surface as 'unselected' in session.

    :param request: request
    :param pk: primary key of the surface
    :return: JSON Response

    The response returns the current selection as suitable for the basket.
    """
    return set_surface_select_status(request, pk, False)


def set_topography_select_status(request, pk, select_status):
    """Marks the given topography as 'selected' or 'unselected' in session.

    :param request: request
    :param pk: primary key of the surface
    :param select_status: True or False, True means "mark as selected", False means "mark as unselected"
    :return: JSON Response

    The response returns the current selection as suitable for the basket.
    """
    try:
        pk = int(pk)
        topo = Topography.objects.get(pk=pk)
        assert topo.surface.has_permission(request.user, "view")
    except (ValueError, Topography.DoesNotExist, AssertionError):
        raise PermissionDenied()  # This should be shown independent of whether the surface exists

    topography_key = _topography_key(pk)
    selection = _selection_set(request)
    is_selected = topography_key in selection

    if request.method == "POST":
        if select_status:
            # topography should be selected
            selection.add(topography_key)
        elif is_selected:
            selection.remove(topography_key)

        request.session["selection"] = list(selection)

    data = current_selection_as_basket_items(request)
    return Response(data)


@api_view(["POST"])
@permission_classes(
    []
)  # We need to override permissions because the anonymous user has read-only access
def select_topography(request, pk):
    """Marks the given topography as 'selected' in session.

    :param request: request
    :param pk: primary key of the surface
    :return: JSON Response

    The response returns the current selection as suitable for the basket.
    """
    return set_topography_select_status(request, pk, True)


@api_view(["POST"])
@permission_classes(
    []
)  # We need to override permissions because the anonymous user has read-only access
def unselect_topography(request, pk):
    """Marks the given topography as 'selected' in session.

    :param request: request
    :param pk: primary key of the surface
    :return: JSON Response

    The response returns the current selection as suitable for the basket.
    """
    return set_topography_select_status(request, pk, False)


def set_tag_select_status(request, pk, select_status):
    """Marks the given tag as 'selected' in session or checks this.

    :param request: request
    :param pk: primary key of the tag
    :param select_status: True if tag should be selected, False if it should be unselected
    :return: JSON Response

    The response returns the current selection as suitable for the basket.
    """
    try:
        pk = int(pk)
        tag = Tag.objects.get(pk=pk)
    except (ValueError, Tag.DoesNotExist):
        raise PermissionDenied()

    if tag not in tags_for_user(request.user):
        raise PermissionDenied()

    tag_key = _tag_key(pk)
    selection = _selection_set(request)
    is_selected = tag_key in selection

    if request.method == "POST":
        if select_status:
            # tag should be selected
            selection.add(tag_key)
        elif is_selected:
            selection.remove(tag_key)

        request.session["selection"] = list(selection)

    data = current_selection_as_basket_items(request)
    return Response(data)


@api_view(["POST"])
@permission_classes(
    []
)  # We need to override permissions because the anonymous user has read-only access
def select_tag(request, pk):
    """Marks the given tag as 'selected' in session.

    :param request: request
    :param pk: primary key of the tag
    :return: JSON Response

    The response returns the current selection as suitable for the basket.
    """
    return set_tag_select_status(request, pk, True)


@api_view(["POST"])
@permission_classes(
    []
)  # We need to override permissions because the anonymous user has read-only access
def unselect_tag(request, pk):
    """Marks the given tag as 'unselected' in session.

    :param request: request
    :param pk: primary key of the tag
    :return: JSON Response

    The response returns the current selection as suitable for the basket.
    """
    return set_tag_select_status(request, pk, False)


@api_view(["POST"])
@permission_classes(
    []
)  # We need to override permissions because the anonymous user has read-only access
def unselect_all(request):
    """Removes all selections from session.

    :param request: request
    :return: empty list as JSON Response
    """
    request.session["selection"] = []
    return Response([])


def extra_tabs_if_single_item_selected(topographies, surfaces):
    """Return contribution to context for opening extra tabs if a single topography/surface is selected.

    Parameters
    ----------
    topographies: list of topographies
        Use here the result of function `utils.selected_instances`.

    surfaces: list of surfaces
        Use here the result of function `utils.selected_instances`.

    Returns
    -------
    Sequence of dicts, each dict corresponds to an extra tab.

    """
    tabs = []

    if len(topographies) == 1 and len(surfaces) == 0:
        # exactly one topography was selected -> show also tabs of topography
        topo = topographies[0]
        tabs.extend(
            [
                {
                    "title": f"{topo.surface.label}",
                    "icon": "gem",
                    "icon_style_prefix": "far",
                    "href": f"{reverse('ce_ui:surface-detail')}?surface={topo.surface.pk}",
                    "active": False,
                    "login_required": False,
                    "tooltip": f"Properties of surface '{topo.surface.label}'",
                },
                {
                    "title": f"{topo.name}",
                    "icon": "file",
                    "icon_style_prefix": "far",
                    "href": f"{reverse('ce_ui:topography-detail')}?topography={topo.pk}",
                    "active": False,
                    "login_required": False,
                    "tooltip": f"Properties of measurement '{topo.name}'",
                },
            ]
        )
    elif len(surfaces) == 1 and all(t.surface == surfaces[0] for t in topographies):
        # exactly one surface was selected -> show also tab of surface
        surface = surfaces[0]
        tabs.append(
            {
                "title": f"{surface.label}",
                "icon": "gem",
                "icon_style_prefix": "far",
                "href": f"{reverse('ce_ui:surface-detail')}?surface={surface.pk}",
                "active": False,
                "login_required": False,
                "tooltip": f"Properties of surface '{surface.label}'",
            }
        )
    return tabs


class AnalysisResultDetailView(DetailView):
    """Show analyses for a given analysis function."""

    model = AnalysisFunction
    template_name = "analysis/analyses_detail.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        function = self.object
        # Check if user is allowed to use this function
        if function.name not in get_analysis_function_names(self.request.user):
            raise PermissionDenied()

        # filter subjects to those this user is allowed to see
        effective_topographies, effective_surfaces, subjects = (
            selection_to_subjects_dict(self.request)
        )

        # get analysis result type
        visualization_type = get_visualization_type(name=function.name)

        context["function"] = function
        context["visualization_type"] = visualization_type

        # Decide whether to open extra tabs for surface/topography details
        tabs = extra_tabs_if_single_item_selected(
            effective_topographies, effective_surfaces
        )
        tabs.extend(
            [
                {
                    "title": "Analyze",
                    "icon": "chart-area",
                    "href": f"{reverse('ce_ui:results-list')}?subjects={self.request.GET.get('subjects')}",
                    "active": False,
                    "login_required": False,
                    "tooltip": "Results for selected analysis functions",
                },
                {
                    "title": f"{function.display_name}",
                    "icon": "chart-area",
                    "href": f"{self.request.path}?subjects={self.request.GET.get('subjects')}",
                    "active": True,
                    "login_required": False,
                    "tooltip": f"Results for analysis '{function.display_name}'",
                    "show_basket": True,
                },
            ]
        )
        context["extra_tabs"] = tabs

        return context


class AnalysesResultListView(TemplateView):
    """View showing analyses from multiple functions."""

    template_name = "analysis/analyses_list.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        topographies = []
        surfaces = []

        # Find out what the subjects are. The usual query is a base64 encoded
        # subjects dictionary passed as the 'subjects' argument.
        subjects = self.request.GET.get("subjects")
        topography = self.request.GET.get("topography")
        surface = self.request.GET.get("surface")
        if subjects is not None:
            try:
                subjects = subjects_from_base64(subjects)
            except:  # noqa: E722
                subjects = None

            if subjects is not None:
                # Update session to reflect selection
                topographies = [t for t in subjects if isinstance(t, Topography)]
                surfaces = [t for t in subjects if isinstance(t, Surface)]
                self.request.session["selection"] = instances_to_selection(
                    topographies=topographies, surfaces=surfaces
                )
        elif topography is not None:
            pass
        elif surface is not None:
            pass

        # Decide whether to open extra tabs for surface/topography details
        tabs = extra_tabs_if_single_item_selected(topographies, surfaces)
        tabs.append(
            {
                "title": "Analyze",
                "icon": "chart-area",
                "icon-style-prefix": "fas",
                "href": f"{reverse('ce_ui:results-list')}?subjects={self.request.GET.get('subjects')}",
                "active": True,
                "login_required": False,
                "tooltip": "Results for selected analysis functions",
                "show_basket": True,
            }
        )
        context["extra_tabs"] = tabs

        return context


class HomeView(TemplateView):
    template_name = "pages/home.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data()
        user = self.request.user
        if user.is_anonymous:
            anon = get_user_model().get_anonymous()
            context["num_users"] = User.objects.filter(
                Q(is_active=True) & ~Q(pk=anon.pk)
            ).count()

            current_stats = current_statistics()
        else:
            current_stats = current_statistics(user)

            # count surfaces you can view, but you are not creator
            context["num_shared_surfaces"] = (
                Surface.objects.for_user(user, "view").exclude(creator=user).count()
            )

        context["num_surfaces"] = current_stats["num_surfaces_excluding_publications"]
        context["num_topographies"] = current_stats[
            "num_topographies_excluding_publications"
        ]
        context["num_analyses"] = current_stats["num_analyses_excluding_publications"]

        return context


class TermsView(TemplateView):
    template_name = "pages/termsconditions.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        active_terms = TermsAndConditions.get_active_terms_list()

        if not self.request.user.is_anonymous:
            context["agreed_terms"] = TermsAndConditions.objects.filter(
                userterms__date_accepted__isnull=False,
                userterms__user=self.request.user,
            ).order_by("date_created")

            context["not_agreed_terms"] = active_terms.filter(
                Q(userterms=None)
                | (
                    Q(userterms__date_accepted__isnull=True)
                    & Q(userterms__user=self.request.user)
                )
            ).order_by("date_created")

        else:
            context["active_terms"] = active_terms.order_by("date_created")

        context["extra_tabs"] = [
            {
                "login_required": False,
                "icon": "file-contract",
                "title": "Terms and Conditions",
                "active": True,
            }
        ]
        context["connect_fixed_tabs_with_extra_tabs"] = False

        return context


#
# The following two views are overwritten from
# termsandconditions package in order to add context
# for the tabbed interface
#
def tabs_for_terms(terms, request_path):
    if len(terms) == 1:
        tab_title = unescape(
            f"{terms[0].name} {terms[0].version_number}"
        )  # mimics '|safe' as in original template
    else:
        tab_title = "Terms"  # should not happen in Topobank, but just to be safe

    return [
        {
            "icon": "file-contract",
            "title": "Terms and Conditions",
            "href": reverse("terms"),
            "active": False,
            "login_required": False,
        },
        {
            "icon": "file-contract",
            "title": tab_title,
            "href": request_path,
            "active": True,
            "login_required": False,
        },
    ]


class TabbedTermsMixin:
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["extra_tabs"] = tabs_for_terms(
            self.get_terms(self.kwargs), self.request.path
        )
        context["connect_fixed_tabs_with_extra_tabs"] = False
        return context


class TermsDetailView(TabbedTermsMixin, OrigTermsView):
    pass


class TermsAcceptView(TabbedTermsMixin, AcceptTermsView):
    pass


class TabbedEmailView(EmailView):
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["extra_tabs"] = [
            {
                "title": "User profile",
                "icon": "user",
                "href": reverse(
                    "ce_ui:user-detail", kwargs=dict(username=self.request.user.username)
                ),
                "active": False,
            },
            {
                "title": "Edit e-mail addresses",
                "icon": "edit",
                "href": self.request.path,
                "active": True,
            },
        ]
        return context


class UserDetailView(LoginRequiredMixin, DetailView):
    model = User
    # These next two lines tell the view to index lookups by username
    slug_field = "username"
    slug_url_kwarg = "username"

    def dispatch(self, request, *args, **kwargs):
        # FIXME! Raise permission denied error if the two users have no shared datasets
        return super().dispatch(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["extra_tabs"] = [
            {
                "title": "User profile",
                "icon": "user",
                "href": self.request.path,
                "active": True,
                "login_required": False,
            }
        ]
        return context


class UserRedirectView(LoginRequiredMixin, RedirectView):
    permanent = False

    def get_redirect_url(self):
        return reverse("ce_ui:user-detail", kwargs={"username": self.request.user.username})


class UserUpdateView(LoginRequiredMixin, UpdateView):
    fields = ["name"]

    # we already imported User in the view code above, remember?
    model = User

    # send the user back to their own page after a successful update

    def get_success_url(self):
        return reverse("ce_ui:user-detail", kwargs={"username": self.request.user.username})

    def get_object(self, queryset=None):
        # Only get the User record for the user making the request
        return User.objects.get(username=self.request.user.username)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["extra_tabs"] = [
            {
                "title": "User Profile",
                "icon": "user",
                "href": reverse(
                    "ce_ui:user-detail", kwargs=dict(username=self.request.user.username)
                ),
                "active": False,
            },
            {
                "title": "Update user",
                "icon": "edit",
                "href": self.request.path,
                "active": True,
            },
        ]
        return context


class UserListView(LoginRequiredMixin, ListView):
    model = User
    # These next two lines tell the view to index lookups by username
    slug_field = "username"
    slug_url_kwarg = "username"
