import json

from django.conf import settings
from django.shortcuts import reverse

from topobank.supplib.versions import get_versions

from .utils import current_selection_as_basket_items

HOME_URL = reverse('home')
SELECT_URL = reverse('ce_ui:select')
UNSELECT_ALL_URL = reverse('ce_ui:unselect-all')


def fixed_tabs_processor(request):
    """Adds fixed tabs.

    Parameters
    ----------
    request

    Returns
    -------
    Dict with extra context, having a key 'fixed_tabs' containing a list of tabs.

    Each tab is a dict with the following form:

    {
        'login_required': True,  # boolean, if True, tab is only shown to logged-in users
        'title': 'Tab title shown on the tab',
        'icon': 'edit',  # a fontawesome icon name,
        'icon_style_prefix': 'fas',  # class used as prefix for icons, default: 'fas' (=solid)
        'href': '',  # A URL pointing to the view for the tab
        'active': False,  #  a boolean; True means the tab is active
    }
    """

    tabs = []
    if settings.TABNAV_DISPLAY_HOME_TAB:
        tabs += [{
            'login_required': False,
            'title': '',  # no text
            'icon': 'home',
            'href': HOME_URL,
            'active': request.path == HOME_URL,
            'tooltip': "Welcome to contact.engineering",
            'show_basket': False,
        }]

    # This is the datasets tab
    tabs += [{
        'login_required': False,
        'title': 'Datasets',
        'icon': 'check-square',
        'icon_style_prefix': 'far',
        'href': SELECT_URL,
        'active': request.path == SELECT_URL,
        'tooltip': "Select surfaces and topographies for analysis or create new surfaces",
        'show_basket': True,
    }]

    # Add default value for icon_style_prefix if missing
    for tab in tabs:
        tab.setdefault('icon_style_prefix', 'fas')

    return dict(fixed_tabs=tabs)


def versions_processor(request):
    return dict(versions=get_versions())


def basket_processor(request):
    """Return JSON with select surfaces and topographies.

    Parameters
    ----------
    request

    Returns
    -------
    Dict with extra context, a key 'basket_items_json'
    which encodes all selected topographies and surfaces such they can be
    displayed on top of each page. See also base.html.
    """
    basket_items = current_selection_as_basket_items(request)

    return dict(basket_items_json=json.dumps(basket_items),
                num_basket_items=len(basket_items),
                unselect_all_url=UNSELECT_ALL_URL)
