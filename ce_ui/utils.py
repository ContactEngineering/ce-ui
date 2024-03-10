import logging

from django.contrib.postgres.search import SearchQuery, SearchVector
from django.core.exceptions import PermissionDenied
from django.db.models import Q, Subquery, TextField, Value
from django.db.models.functions import Replace
from guardian.shortcuts import get_users_with_perms
from rest_framework.reverse import reverse
from topobank.manager.models import Surface, Tag, Topography
from topobank.manager.utils import subjects_to_dict, surfaces_for_user

_log = logging.getLogger(__name__)

DEFAULT_DATASOURCE_NAME = 'Default'
MAX_LEN_SEARCH_TERM = 200
SELECTION_SESSION_VARNAME = 'selection'


def selection_from_session(session):
    """Get selection from session.

    The selection is a list of strings like

    [ 'topography-1', 'surface-4']

    which represents the selected objects.
    """
    return session.get(SELECTION_SESSION_VARNAME, [])


def instances_to_selection(topographies=[], surfaces=[], tags=[]):
    """Returns a list of strings suitable for selecting instances.

    :param topographies: sequence of Topography instances
    :param surfaces: sequence of Surface instances
    :param tags: sequence of Tag instances
    :return: list of str, alphabetically sorted
    """
    selection = []
    for topo in topographies:
        if topo.surface in surfaces:
            # will be included by surface
            continue
        selection.append(f'topography-{topo.id}')

    for surf in surfaces:
        selection.append(f'surface-{surf.id}')

    for tag in tags:
        selection.append(f'tag-{tag.id}')

    return sorted(selection)


def instances_to_topographies(topographies, surfaces, tags):
    """Returns a queryset of topographies, based on given instances

    Given topographies, surfaces and tags are resolved and
    all topographies are returned which are either
    - explicitly given
    - given indirectly by a surface
    - given indirectly by a tag, if the topography is tagged accordingly
    - given indirectly by a tag, if its surface is tagged accordingly

    Parameters
    ----------
    topographies: sequence of topographies
    surfaces: sequence of surfaces
    tags: sequence of tags

    Returns
    -------
    Queryset of topography, distinct
    """
    topography_ids = [topo.id for topo in topographies]
    surface_ids = [s.id for s in surfaces]
    tag_ids = [tag.id for tag in tags]

    topographies = Topography.objects.filter(id__in=topography_ids)
    topographies |= Topography.objects.filter(surface__in=surface_ids)
    topographies |= Topography.objects.filter(surface__tags__in=tag_ids)
    topographies |= Topography.objects.filter(tags__in=tag_ids)

    return topographies.distinct().order_by('id')


def instances_to_surfaces(surfaces, tags):
    """Returns a queryset of surfaces, based on given instances

    Given surfaces and tags are resolved and
    all surfaces are returned which are either
    - explicitly given
    - given indirectly by a tag, if the surface is tagged accordingly

    Parameters
    ----------
    surfaces: sequence of surfaces
    tags: sequence of tags

    Returns
    -------
    Queryset of surface, distinct
    """
    surface_ids = [s.id for s in surfaces]
    tag_ids = [tag.id for tag in tags]

    surfaces = Surface.objects.filter(id__in=surface_ids)
    surfaces |= Surface.objects.filter(tags__in=tag_ids)

    return surfaces.distinct().order_by('id')


def selection_to_instances(selection):
    """Returns a tuple with querysets of explicitly selected topographies, surfaces, and tags.

    View permission is not checked.

    :param selection: selection list as saved in session
    :return: tuple (topographies, surfaces, tags)

    The returned tuple has 3 elements:

     'topographies': all topographies explicitly found in the selection
     'surfaces': all surfaces explicitly found in the selection (not only because its topography was selected)
     'tags': all tags explicitly found in the selection (not only because all related items are selected)

    Also surfaces without topographies are returned in 'surfaces' if selected.
    """
    topography_ids = set()
    surface_ids = set()
    tag_ids = set()

    for type_id in selection:
        type, id = type_id.split('-')
        id = int(id)
        if type == 'topography':
            topography_ids.add(id)
        elif type == 'surface':
            surface_ids.add(id)
        elif type == 'tag':
            tag_ids.add(id)

    topographies = Topography.objects.filter(id__in=topography_ids)
    surfaces = Surface.objects.filter(id__in=surface_ids)
    tags = Tag.objects.filter(id__in=tag_ids)

    return topographies, surfaces, tags


def selected_instances(request):
    """Return a tuple with topography, surface, and tag instances which are currently selected.

    View permission is checked for the user of the request.

    :request: HTTP request
    :return: tuple (topographies, surfaces, tags)

    The returned tuple has 3 elements, each a list:

     'topographies': all topographies in the selection
     'surfaces': all surfaces explicitly found in the selection (not only because its topography was selected)
     'tags': all tags explicitly found in selection (not because all tagged items are selected)

    Also surfaces without topographies are returned in 'surfaces' if selected.

    If only one topography is selected, it's surface is *not* returned in 'surfaces'.
    If a surface is explicitly selected, all of its topographies are contained in 'topographies'.
    """
    selection = selection_from_session(request.session)
    topographies, surfaces, tags = selection_to_instances(selection)

    # make sure that only topographies with read permission can be found here
    unique_surfaces = set(t.surface for t in topographies) | set(surfaces)
    surfaces_with_view_permission = [s for s in unique_surfaces if request.user.has_perm('view_surface', s)]
    topographies = [t for t in topographies if t.surface in surfaces_with_view_permission]
    surfaces = [s for s in surfaces if s in surfaces_with_view_permission]

    return topographies, surfaces, list(tags)


def current_selection_as_surface_list(request):
    """Returns a list of surfaces related to the current selection.

    For all selected items, surfaces, topographies, or tags
    the surface is identified which contains the selected data.
    In the result, each of those surfaces is included once.

    :param request: current request
    :return: list of Surface instances, sorted by name
    """
    topographies, surfaces, tags = selected_instances(request)

    #
    # Collect all surfaces related to the selected items in a set
    #
    surfaces = set(surfaces)
    for topo in topographies:
        surfaces.add(topo.surface)
    for tag in tags:
        related_objects = tag.get_related_objects(flat=True)
        for obj in related_objects:
            if isinstance(obj, Surface):
                surfaces.add(obj)
            elif hasattr(obj, 'surface'):
                surfaces.add(obj.surface)
    #
    # Filter surfaces such that the requesting user has permissions to read
    #
    surfaces = [surf for surf in surfaces if request.user.has_perm('view_surface', surf)]
    surfaces.sort(key=lambda s: s.name)

    return surfaces


def instances_to_basket_items(topographies, surfaces, tags):
    """

    Parameters
    ----------
    topographies
    surfaces
    tags

    Returns
    -------
    List of items in the basket. Each is a dict with keys

     label, type, unselect_url, key

    Example with one selected surface:

     [ {'label': "Test Surface",
        'type': "surface",
        'unselect_url': ".../manager/surface/13/unselect",
        'key': "surface-13"}
     ]

    """
    basket_items = []
    for surface in surfaces:
        unselect_url = reverse('ce_ui:surface-unselect', kwargs=dict(pk=surface.pk))
        basket_items.append(dict(label=str(surface),
                                 type="surface",
                                 id=surface.pk,
                                 unselect_url=unselect_url,
                                 key=f"surface-{surface.pk}"))
    for topography in topographies:
        unselect_url = reverse('ce_ui:topography-unselect', kwargs=dict(pk=topography.pk))
        basket_items.append(dict(label=topography.name,
                                 type="topography",
                                 id=topography.pk,
                                 unselect_url=unselect_url,
                                 key=f"topography-{topography.pk}",
                                 surface_key=f"surface-{topography.surface.pk}"))
    for tag in tags:
        unselect_url = reverse('ce_ui:tag-unselect', kwargs=dict(pk=tag.pk))
        basket_items.append(dict(label=tag.name,
                                 type="tag",
                                 id=tag.pk,
                                 unselect_url=unselect_url,
                                 key=f"tag-{tag.pk}"))

    return basket_items


def current_selection_as_basket_items(request):
    """Returns current selection as JSON suitable for the basket.

    Parameters
    ----------
    request

    Returns
    -------
    List of items in the basket. Each is a dict with keys

     label, type, unselect_url, key

    Example with one selected surface:

     [ {'label': "Test Surface",
        'type': "surface",
        'unselect_url': ".../manager/surface/13/unselect",
        'key': "surface-13"}
     ]

    """
    topographies, surfaces, tags = selected_instances(request)
    return instances_to_basket_items(topographies, surfaces, tags)


def filter_queryset_by_search_term(qs, search_term, search_fields):
    """Filter queryset for a given search term.

    Parameters
    ----------
    qs : QuerySet
        QuerySet which should be additionally filtered by a search term.
    search_term: str
        Search term entered by the user. Can be an expression.
        See https://docs.djangoproject.com/en/3.2/ref/contrib/postgres/search/
        for details.
    search_fields: list of str
        ORM expressions which refer to search fields, e.g. "description"
        or "topography__description" for the description field of a child object

    Returns
    -------
    Filtered query set.
    """
    return qs.annotate(
        search=SearchVector(*search_fields, config='english')
    ).filter(
        search=SearchQuery(search_term, config="english", search_type='websearch')
        # search__icontains=search_term  # alternative, which finds substrings but does not allow for expressions
    ).distinct('id').order_by('id')


def filtered_topographies(request, surfaces):
    """Return topographies which match a request.

    Parameters
    ----------
    request
    surfaces
        queryset with surfaces which already match

    Returns
    -------
    queryset with matching topographies

    """
    topographies = Topography.objects.filter(surface__in=surfaces)

    #
    # Search results
    #
    search_term = get_search_term(request)
    if search_term:
        # We introduce an extra field for search in tag names where the tag names
        # are changed so that the tokenizer splits the names into multiple words
        topographies = topographies.annotate(
            tag_names_for_search=Replace(
                Replace('tags__name', Value('.'), Value(' ')),  # replace . with space
                Value('/'), Value(' ')),  # replace / with space
            name_for_search=Replace('name', Value('.'), Value(' '), output_field=TextField())
        ).distinct('id').order_by('id')
        topographies = filter_queryset_by_search_term(topographies, search_term, [
            'description', 'creator__name', 'name_for_search', 'tag_names_for_search',
        ])

    #
    # Sort results
    #
    order_by = get_order_by(request)
    topographies = Topography.objects.filter(
        pk__in=Subquery(topographies.values('pk'))
    ).order_by(order_by)

    return topographies


def tags_for_user(user, surfaces=None, topographies=None):
    """Return set of tags which can be used for autocomplete when editing tags.

    A user should not see all tags ever used on the app, but only those
    which were chosen by herself or collaborators and corresponding parent tags.

    :param user: User instance
    :param surfaces: surfaces to use, if None,
                     will be computed for given user; specify this to reuse previous calculation
                     or to reduce number of surfaces based on a request
    :param topographies: topographies to use, if None,
                     will be computed from surfaces; specify this to reuse previous calculation
                     or to reduce number of topographies based on a request
    :return: list of strings
    """
    if surfaces is None:
        surfaces = surfaces_for_user(user)
    if topographies is None:
        topographies = Topography.objects.filter(surface__in=surfaces)

    tags = Tag.objects.filter(Q(surface__in=surfaces) | Q(topography__in=topographies))

    # add parent tags not already included
    for t in tags:
        tags |= t.get_ancestors()

    return tags.distinct()


def selection_to_subjects_dict(request):
    """Convert current selection into list of subjects as json.

    Parameters
    ----------
    request

    Returns
    -------
    (eff_topographies, eff_surfaces, subjects_ids_json)

    where:
        eff_topographies       - list of topographies which are effectively
                                 included in the selection (selected explicitly
                                 or implicitly by surfaces and tags)
        eff_surfaces           - list of surfaces which are effectively
                                  included in the selection (by selecting surfaces+tags)
        subjects_ids_json - JSONfied dict with key: content type id, value: list of object ids
                            This dict encodes all subjects in the selection

    The eff_ results can be used for selection which tabs should be shown in the UI.
    This was the original purpose for returning them here.
    """
    topographies, surfaces, tags = selected_instances(request)
    effective_topographies = instances_to_topographies(topographies, surfaces, tags)
    effective_surfaces = instances_to_surfaces(surfaces, tags)

    # Do we have permission for all of these?
    user = request.user
    unique_surfaces = set(t.surface for t in effective_topographies) | set(effective_surfaces)
    surfaces_with_view_permission = [s for s in unique_surfaces if user.has_perm('view_surface', s)]
    effective_topographies = [t for t in effective_topographies if t.surface in surfaces_with_view_permission]
    effective_surfaces = [s for s in effective_surfaces if s in surfaces_with_view_permission]

    # we collect effective topographies and surfaces because we have so far implementations
    # for analysis functions for topographies and surfaces
    subjects_ids = subjects_to_dict(effective_topographies + effective_surfaces)

    return effective_topographies, effective_surfaces, subjects_ids


def get_search_term(request) -> str:
    """Extract a search term from given request.

    The search term is truncated at a maximum
    size of MAX_LEN_SEARCH_TERM.

    Parameters
    ----------
    request

    Returns
    -------
    String with search term, an empty string if no term was given.

    """
    print('GET', request.GET)
    search_term = request.GET.get('search', default='')
    search_term = search_term[:MAX_LEN_SEARCH_TERM]
    return search_term.strip()


def get_category(request) -> str:
    """Extract a surface category from given request.

    Parameters
    ----------
    request

    Returns
    -------
    String with requested category.

    Raises
    ------
    PermissionDenied() if an unknown category was given.
    """
    from .views import CATEGORY_FILTER_CHOICES
    category = request.GET.get('category', default='all')
    if category not in CATEGORY_FILTER_CHOICES.keys():
        raise PermissionDenied()
    return category


def get_order_by(request) -> str:
    """Extract sort by from given request.
    Parameters
    ----------
    request

    Returns
    -------
    Sorted with requested sort by.
    """
    from .views import ORDER_BY_CHOICES
    order_by = request.GET.get('order_by', default='date')
    if order_by not in ORDER_BY_CHOICES.keys():
        order_by = 'name'
    return order_by


def get_sharing_status(request) -> str:
    """Extract a sharing status from given request.

     Parameters
     ----------
     request

     Returns
     -------
     String with requested sharing status.

     Raises
     ------
     PermissionDenied() if an unknown sharing status was given.
     """
    from .views import SHARING_STATUS_FILTER_CHOICES
    sharing_status = request.GET.get('sharing_status', default='all')
    if sharing_status not in SHARING_STATUS_FILTER_CHOICES.keys():
        raise PermissionDenied()
    return sharing_status


def get_tree_mode(request) -> str:
    """Extract tree_mode from given request.

     Parameters
     ----------
     request

     Returns
     -------
     String with requested tree mode.

     Raises
     ------
     PermissionDenied() if an unknown sharing status was given.
     """
    from .views import TREE_MODE_CHOICES
    tree_mode = request.GET.get('tree_mode', default='surface list')
    if tree_mode not in TREE_MODE_CHOICES:
        raise PermissionDenied()
    return tree_mode


def get_permission_table_data(instance, request_user, actions=['view', 'change', 'delete', 'share']):
    """Prepare data for a permission table.

    Parameters
    ----------
    instance: Model
        Model instance for which the permission table should be generated.
    request_user: User
        User for which the permission table is prepared.
    actions: list of str
        Action for which permission may be given. Example: ['view', 'change', 'delete', 'share']

    Returns
    -------
    List of tuples for cells. Each cell is represented by a 4-tuple

       (user_display_name, user_url, allowed, description)

    where

        user_display_name: name of the user
        user_url: URL to user details
        allowed: boolean which is true, when allowed
        description: a str with verbal description of this entry for tooltips.

    """
    perms = get_users_with_perms(instance, attach_perms=True)
    # is now a dict of the form
    #  <User: joe>: ['view_surface'], <User: dan>: ['view_surface', 'change_surface']}
    allowed_users = sorted(perms.keys(), key=lambda u: u.name if u else '')

    # convert to list of boolean based on list ACTIONS
    #
    # Each table element here is a 2-tuple: (cell content, cell title)
    #
    # The cell content is inserted into the cell.
    # The cell title is shown in a tooltip and can be used in tests.
    #
    perm_postfix = type(instance).__name__.lower()
    perms_table = []
    for user in allowed_users:

        if user == request_user:
            user_display_name = "You"
            auxiliary = "have"
        else:
            user_display_name = user.name
            auxiliary = "has"

        # the current user is represented as None, can be displayed in a special way in template ("You")
        row = [(user_display_name, user.get_absolute_url())]  # cell title is used for passing a link here
        for act in actions:

            perm = act + '_' + perm_postfix
            has_perm = perm in perms[user]

            cell_title = "{} {}".format(user_display_name, auxiliary)
            if not has_perm:
                cell_title += "n't"
            cell_title += " the permission to {} this surface".format(act)

            row.append((has_perm, cell_title))

        perms_table.append(row)

    return perms_table
