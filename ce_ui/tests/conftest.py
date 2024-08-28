import pytest
from topobank.testing.factories import OrganizationFactory  # noqa: F401
from topobank.testing.factories import UserFactory
from topobank.testing.fixtures import handle_usage_statistics  # noqa: F401
from topobank.testing.fixtures import sync_analysis_functions  # noqa: F401
from topobank.testing.fixtures import test_analysis_function  # noqa: F401
from topobank.testing.fixtures import two_topos  # noqa: F401
from topobank.testing.fixtures import \
    user_three_topographies_three_surfaces_three_tags  # noqa: F401

from .fixtures import orcid_socialapp  # noqa: F401


@pytest.mark.django_db
@pytest.fixture
def user_with_plugin():
    org_name = "Test Organization"
    org = OrganizationFactory(name=org_name, plugins_available="ce_ui")
    user = UserFactory()
    user.groups.add(org.group)
    return user
