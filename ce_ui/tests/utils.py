from django.shortcuts import reverse
from topobank.manager.views import SurfaceViewSet
from topobank.testing.utils import ordereddicts_to_dicts


def search_surfaces(request_factory, user, expr):
    """Search surfaces with given expression and return dicts with results.

    This is a helper function used in tests.

    Parameters
    ----------
    request_factory: rest_framework.test.APIRequestFactory
        Used to generate a search request
    user: topobank.users.models.User
        This is the user who performs the search.
    expr: str
        Search expression.

    Returns
    -------
    List of dicts with search results, sorted by 'title' key.
    """
    request = request_factory.get(reverse('manager:surface-api-list') + f"?search={expr}")
    request.user = user
    request.session = {}  # must be there
    response = SurfaceViewSet.as_view()(request)
    assert response.status_code == 200
    return ordereddicts_to_dicts(response.data['results'], sorted_by='title')
