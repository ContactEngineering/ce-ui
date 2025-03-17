import logging
from html import unescape

from allauth.account.views import EmailView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.core.exceptions import PermissionDenied
from django.db.models import Q
from django.urls import reverse
from django.views.generic import (DetailView, ListView, RedirectView,
                                  TemplateView, UpdateView)
from termsandconditions.models import TermsAndConditions
from termsandconditions.views import AcceptTermsView
from topobank.analysis.models import AnalysisFunction
from topobank.analysis.registry import get_analysis_function_names
from topobank.analysis.serializers import WorkflowSerializer
from topobank.manager.models import Surface, Topography
from topobank.manager.serializers import (SurfaceSerializer,
                                          TopographySerializer)
from topobank.manager.utils import subjects_from_base64, subjects_to_base64
from topobank.usage_stats.utils import increase_statistics_by_date
from topobank.users.models import User
from trackstats.models import Metric, Period

from ce_ui import breadcrumb

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
        context["serialized_object"] = self.get_serializer_class()(
            self.object, context={"request": self.request}
        ).data
        print(context["serialized_object"])

        return context


class DataSetListView(AppView):
    vue_component = "DatasetList"

    def dispatch(self, request, *args, **kwargs):
        # count this view event for statistics
        metric = Metric.objects.SEARCH_VIEW_COUNT
        increase_statistics_by_date(metric, period=Period.DAY)
        return super().dispatch(request, *args, **kwargs)


class DatasetDetailView(AppDetailView):
    model = Surface
    vue_component = "DatasetDetail"
    serializer_class = SurfaceSerializer

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        #
        # Check permissions
        #
        if not self.object.has_permission(self.request.user, "view"):
            raise PermissionDenied()

        #
        # Breadcrumb navigation
        #
        breadcrumb.add_surface(context, self.object)

        return context


class DatasetPublishView(AppDetailView):
    model = Surface
    vue_component = "DatasetPublish"
    serializer_class = SurfaceSerializer

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        #
        # Check permissions
        #
        if not self.object.has_permission(self.request.user, "full"):
            raise PermissionDenied()

        #
        # Breadcrumb navigation
        #
        breadcrumb.add_surface(context, self.object)
        breadcrumb.add_generic(
            context,
            {
                "title": "Publish dataset",
                "icon": "paper-plane",
                "icon_style_prefix": "far",
                "href": f"{reverse('ce_ui:dataset-publish', kwargs=dict(pk=self.object.id))}",
                "active": True,
                "login_required": False,
                "tooltip": f"Publish '{self.object.label}'",
            },
        )

        return context


class TopographyDetailView(AppDetailView):
    model = Topography
    vue_component = "TopographyDetail"
    serializer_class = TopographySerializer

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        #
        # Check permissions
        #
        if not self.object.has_permission(self.request.user, "view"):
            raise PermissionDenied()

        #
        # Breadcrumb navigation
        #
        breadcrumb.add_surface(context, self.object.surface)
        breadcrumb.add_topography(context, self.object)

        return context


def extra_tabs_if_single_item_selected(context, subjects):
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
    surfaces = [x for x in subjects if isinstance(x, Surface)]
    topographies = [x for x in subjects if isinstance(x, Topography)]
    if len(topographies) == 1 and len(surfaces) == 0:
        # exactly one topography was selected -> show also tabs of topography
        topo = topographies[0]
        breadcrumb.add_generic(
            context,
            {
                "title": f"{topo.surface.label}",
                "icon": "gem",
                "icon_style_prefix": "far",
                "href": f"{reverse('ce_ui:surface-detail', kwargs=dict(pk=topo.surface.pk))}",
                "active": False,
                "login_required": False,
                "tooltip": f"Properties of surface '{topo.surface.label}'",
            },
        )
        breadcrumb.add_generic(
            context,
            {
                "title": f"{topo.name}",
                "icon": "file",
                "icon_style_prefix": "far",
                "href": f"{reverse('ce_ui:topography-detail', kwargs=dict(pk=topo.pk))}",
                "active": False,
                "login_required": False,
                "tooltip": f"Properties of measurement '{topo.name}'",
            },
        )
    elif len(surfaces) == 1 and all(t.surface == surfaces[0] for t in topographies):
        # exactly one surface was selected -> show also tab of surface
        surface = surfaces[0]
        breadcrumb.add_generic(
            context,
            {
                "title": f"{surface.label}",
                "icon": "gem",
                "icon_style_prefix": "far",
                "href": f"{reverse('ce_ui:surface-detail', kwargs=dict(pk=surface.pk))}",
                "active": False,
                "login_required": False,
                "tooltip": f"Properties of surface '{surface.label}'",
            },
        )


class AnalysisDetailView(AppDetailView):
    model = AnalysisFunction
    slug_field = "name"
    vue_component = "AnalysisDetail"
    serializer_class = WorkflowSerializer

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        workflow = self.object
        # Check if user is allowed to use this function
        if workflow.name not in get_analysis_function_names(self.request.user):
            raise PermissionDenied()

        # Decide whether to open extra tabs for surface/topography details
        subjects = subjects_from_base64(
            self.request.GET.get("subjects"), user=self.request.user
        )
        extra_tabs_if_single_item_selected(context, subjects)
        subjects = subjects_to_base64(subjects)
        breadcrumb.add_generic(
            context,
            {
                "title": "Analyze",
                "icon": "chart-area",
                "href": f"{reverse('ce_ui:results-list')}?subjects={subjects}",
                "active": False,
                "login_required": False,
                "tooltip": "Results for selected workflow",
            },
        )
        breadcrumb.add_generic(
            context,
            {
                "title": f"{workflow.display_name}",
                "icon": "chart-area",
                "href": f"{self.request.path}?subjects={subjects}",
                "active": True,
                "login_required": False,
                "tooltip": f"Results for workflow '{workflow.display_name}'",
                "show_basket": True,
            },
        )

        return context


class AnalysisListView(AppView):
    vue_component = "AnalysisList"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        subjects = subjects_from_base64(
            self.request.GET.get("subjects"), user=self.request.user
        )
        extra_tabs_if_single_item_selected(context, subjects)

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
    vue_component = "Home"


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


class TermsDetailView(TabbedTermsMixin, TermsView):
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
