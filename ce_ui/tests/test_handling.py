import datetime
import yaml
import zipfile
from io import BytesIO

import pytest

from django.shortcuts import reverse
from django.conf import settings
from rest_framework.test import APIRequestFactory

from trackstats.models import Metric, Period

from topobank.manager.tests.utils import SurfaceFactory, Topography1DFactory, Topography2DFactory, UserFactory

from ..views import DEFAULT_CONTAINER_FILENAME


@pytest.mark.django_db
def test_download_selection(client, mocker, handle_usage_statistics):
    record_mock = mocker.patch('trackstats.models.StatisticByDateAndObject.objects.record')

    user = UserFactory()
    surface1 = SurfaceFactory(creator=user)
    surface2 = SurfaceFactory(creator=user)
    topo1a = Topography1DFactory(surface=surface1)
    Topography2DFactory(surface=surface1)
    Topography1DFactory(surface=surface2)

    factory = APIRequestFactory()

    request = factory.get(reverse('ce_ui:download-selection'))
    request.user = user
    request.session = {
        'selection': [f'topography-{topo1a.id}', f'surface-{surface2.id}']
    }
    from ..views import download_selection_as_surfaces
    response = download_selection_as_surfaces(request)
    assert response.status_code == 200, response.reason
    assert response['Content-Disposition'] == f'attachment; filename="{DEFAULT_CONTAINER_FILENAME}"'

    # open zip file and look into meta file, there should be two surfaces and three topographies
    with zipfile.ZipFile(BytesIO(response.content)) as zf:
        meta_file = zf.open('meta.yml')
        meta = yaml.safe_load(meta_file)
        assert len(meta['surfaces']) == 2
        assert len(meta['surfaces'][0]['topographies']) == 2
        assert len(meta['surfaces'][1]['topographies']) == 1

    # each downloaded surface is counted once
    metric = Metric.objects.SURFACE_DOWNLOAD_COUNT
    today = datetime.date.today()
    if settings.ENABLE_USAGE_STATS:
        record_mock.assert_any_call(metric=metric, object=surface1, period=Period.DAY,
                                    value=1, date=today)
        record_mock.assert_any_call(metric=metric, object=surface2, period=Period.DAY,
                                    value=1, date=today)


#######################################################################
# Selections
#######################################################################

@pytest.mark.django_db
def test_empty_surface_selection(client, handle_usage_statistics):
    #
    # database objects
    #
    user = UserFactory()
    surface = SurfaceFactory(creator=user)
    assert surface.topography_set.count() == 0

    client.force_login(user)

    client.post(reverse('ce_ui:surface-select', kwargs=dict(pk=surface.pk)))

    #
    # Now the selection should contain one empty surface
    #
    assert client.session['selection'] == [f'surface-{surface.pk}']
