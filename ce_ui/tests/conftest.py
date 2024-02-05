import pytest

from topobank.fixtures import handle_usage_statistics, sync_analysis_functions, test_analysis_function  # noqa: F401
from topobank.manager.tests.utils import two_topos, user_three_topographies_three_surfaces_three_tags, \
    UserFactory  # noqa: F401
from topobank.organizations.tests.utils import OrganizationFactory

from .fixtures import orcid_socialapp  # noqa: F401


@pytest.mark.django_db
@pytest.fixture
def user_with_plugin():
    org_name = "Test Organization"
    org = OrganizationFactory(name=org_name, plugins_available="ce_ui")
    user = UserFactory()
    user.groups.add(org.group)
    return user
