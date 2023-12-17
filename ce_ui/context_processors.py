from django.conf import settings
from django.shortcuts import reverse
from django.templatetags.static import static
import django

import json
import celery
import numpy
import scipy

import SurfaceTopography, ContactMechanics, NuMPI, muFFT

import topobank

from .utils import current_selection_as_basket_items

HOME_URL = reverse('home')
SELECT_URL = reverse('manager:select')
UNSELECT_ALL_URL = reverse('manager:unselect-all')


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
    # key 'links': dicts with keys display_name:url
    versions = [
        dict(module='TopoBank',
             version=topobank.__version__,
             license=('MIT', 'https://github.com/ContactEngineering/topobank/blob/develop/LICENSE'),
             links={'Website': 'https://github.com/ComputationalMechanics/TopoBank',
                    'Changelog': static('other/CHANGELOG.md')}),  # needs 'manage.py collectstatic' before!
        dict(module='SurfaceTopography',
             version=SurfaceTopography.__version__,
             license=('MIT', 'https://github.com/ContactEngineering/SurfaceTopography/blob/master/LICENSE.md'),
             links={'Website': 'https://github.com/ComputationalMechanics/SurfaceTopography',
                    'Changelog': f'https://github.com/ComputationalMechanics/SurfaceTopography/blob/{SurfaceTopography.__version__}/SurfaceTopography/ChangeLog.md'}),
        dict(module='ContactMechanics',
             version=ContactMechanics.__version__,
             license=('MIT', 'https://github.com/ContactEngineering/ContactMechanics/blob/master/LICENSE.md'),
             links={'Website': 'https://github.com/ComputationalMechanics/ContactMechanics',  #
                    'Changelog': f'https://github.com/ComputationalMechanics/ContactMechanics/blob/{ContactMechanics.__version__}/ContactMechanics/ChangeLog.md'}),
        dict(module='NuMPI',
             version=NuMPI.__version__,
             license=('MIT', 'https://github.com/IMTEK-Simulation/NuMPI/blob/master/LICENCE.md'),
             links={'Website': 'https://github.com/IMTEK-Simulation/NuMPI',
                    'Changelog': f'https://github.com/IMTEK-Simulation/NuMPI/blob/{NuMPI.__version__}/ChangeLog.md'}),
        dict(module='muFFT',
             version=muFFT.version.description(),
             license=('LGPL-3', 'https://gitlab.com/muspectre/muspectre/-/blob/master/LICENSE'),
             links={'Website': 'https://gitlab.com/muspectre/muspectre',
                    'Changelog': f'https://gitlab.com/muspectre/muspectre/-/blob/{muFFT.version.description()}/CHANGELOG.md'}),
        dict(module='NumPy',
             version=numpy.__version__,
             license=('BSD 3-Clause', 'https://github.com/numpy/numpy/blob/main/LICENSE.txt'),
             links={'Website': 'https://numpy.org/'}),
        dict(module='SciPy',
             version=scipy.__version__,
             license=('BSD 3-Clause', 'https://github.com/scipy/scipy/blob/main/LICENSE.txt'),
             links={'Website': 'https://www.scipy.org/'}),
        dict(module='Django',
             version=django.__version__,
             license=('BSD 3-Clause', 'https://github.com/django/django/blob/main/LICENSE'),
             links={'Website': 'https://www.djangoproject.com/'}),
        dict(module='Celery',
             version=celery.__version__,
             license=('BSD 3-Clause', 'https://github.com/celery/celery/blob/main/LICENSE'),
             links={'Website': 'http://www.celeryproject.org/'})
    ]

    return dict(versions=versions, contact_email_address=settings.CONTACT_EMAIL_ADDRESS)


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
