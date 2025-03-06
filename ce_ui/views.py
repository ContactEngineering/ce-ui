import logging
from html import unescape
from io import BytesIO

from allauth.account.views import EmailView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.core.exceptions import PermissionDenied
from django.db.models import Q, Subquery, TextField, Value
from django.db.models.functions import Replace
from django.http import HttpResponse
from django.urls import reverse
from django.views.generic import (DetailView, ListView, RedirectView,
                                  TemplateView, UpdateView)
from termsandconditions.models import TermsAndConditions
from termsandconditions.views import AcceptTermsView
from termsandconditions.views import TermsView as OrigTermsView
from topobank.analysis.models import AnalysisFunction
from topobank.analysis.registry import get_analysis_function_names
from topobank.analysis.serializers import WorkflowSerializer
from topobank.manager.containers import write_surface_container
from topobank.manager.models import Surface, Topography
from topobank.manager.serializers import SurfaceSerializer
from topobank.manager.utils import subjects_from_base64
from topobank.usage_stats.utils import (increase_statistics_by_date,
                                        increase_statistics_by_date_and_object)
from topobank.users.models import User
from trackstats.models import Metric, Period

from ce_ui import breadcrumb

from .utils import (filter_queryset_by_search_term, get_order_by,
                    get_search_term, get_sharing_status,
                    instances_to_selection)

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


class AppView(TemplateView):
    template_name = "app.html"
    vue_component = None

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        context["vue_component"] = self.vue_component
        context["extra_tabs"] = []

        return context


class AppDetailView(DetailView):
    template_name = "app.html"
    vue_component = None
    serializer_class = None

    def get_serializer_class(self):
        return self.serializer_class

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        context["vue_component"] = self.vue_component
        context["extra_tabs"] = []
        context["object_json"] = self.get_serializer_class()(self.object).data

        return context


class DataSetListView(AppView):
    vue_component = "dataset-list"

    def dispatch(self, request, *args, **kwargs):
        # count this view event for statistics
        metric = Metric.objects.SEARCH_VIEW_COUNT
        increase_statistics_by_date(metric, period=Period.DAY)
        return super().dispatch(request, *args, **kwargs)


class DatasetDetailView(AppDetailView):
    model = Surface
    vue_component = "dataset-detail"
    serializer_class = SurfaceSerializer

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


class TopographyDetailView(AppView):
    vue_component = "topography-detail"

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


class AnalysisDetailView(AppDetailView):
    model = AnalysisFunction
    vue_component = "AnalysisDetail"
    serializer_class = WorkflowSerializer

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        function = self.object
        # Check if user is allowed to use this function
        if function.name not in get_analysis_function_names(self.request.user):
            raise PermissionDenied()

        # Decide whether to open extra tabs for surface/topography details
        breadcrumb.add_generic(
            context,
            {
                "title": "Analyze",
                "icon": "chart-area",
                "href": f"{reverse('ce_ui:results-list')}?subjects={self.request.GET.get('subjects')}",
                "active": False,
                "login_required": False,
                "tooltip": "Results for selected analysis functions",
            },
        )
        breadcrumb.add_generic(
            context,
            {
                "title": f"{function.display_name}",
                "icon": "chart-area",
                "href": f"{self.request.path}?subjects={self.request.GET.get('subjects')}",
                "active": True,
                "login_required": False,
                "tooltip": f"Results for analysis '{function.display_name}'",
                "show_basket": True,
            },
        )

        return context


class AnalysisListView(AppView):
    vue_component = "analysis-list"

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
        # extra_tabs_if_single_item_selected(context, topographies, surfaces)
        breadcrumb.add_generic(
            context,
            {
                "title": "Analyze",
                "icon": "chart-area",
                "icon-style-prefix": "fas",
                "href": f"{reverse('ce_ui:results-list')}?subjects={self.request.GET.get('subjects')}",
                "active": True,
                "login_required": False,
                "tooltip": "Results for selected analysis functions",
                "show_basket": True,
            },
        )

        return context


class HomeView(AppView):
    vue_component = "home"


class TermsView(TemplateView):
    template_name = "apps/termsconditions.html"

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
                    "ce_ui:user-detail",
                    kwargs=dict(username=self.request.user.username),
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
        return reverse(
            "ce_ui:user-detail", kwargs={"username": self.request.user.username}
        )


class UserUpdateView(LoginRequiredMixin, UpdateView):
    fields = ["name"]

    # we already imported User in the view code above, remember?
    model = User

    # send the user back to their own page after a successful update

    def get_success_url(self):
        return reverse(
            "ce_ui:user-detail", kwargs={"username": self.request.user.username}
        )

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
                    "ce_ui:user-detail",
                    kwargs=dict(username=self.request.user.username),
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
