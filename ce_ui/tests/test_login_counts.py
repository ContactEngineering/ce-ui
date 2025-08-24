import datetime

import pytest
from freezegun import freeze_time
from topobank.testing.factories import UserFactory
from trackstats.models import Metric, StatisticByDate

from ce_ui.signals import track_user_login


@pytest.mark.django_db
def test_login_statistics(client):

    today = datetime.date.today()

    user1 = UserFactory()
    user2 = UserFactory()

    client.force_login(user1)
    client.logout()

    client.force_login(user2)
    client.logout()

    # Signal is not called for some reason - calling signal handler manually
    track_user_login(sender=user2.__class__, today=today)

    #
    # There should be two logins for two users now for today
    #
    m = Metric.objects.USERS_LOGIN_COUNT
    s = StatisticByDate.objects.get(metric=m, date=today)
    assert s.value == 2

    #
    # Check also for a specific day
    #
    yesterday = today - datetime.timedelta(1)

    with freeze_time(yesterday):
        client.force_login(user1)
        client.logout()
        track_user_login(sender=user1.__class__)

        #
        # There should be one login for one user for yesterday
        #
        s = StatisticByDate.objects.get(metric=m, date=yesterday)
        assert s.value == 1

        #
        # There should be still those logins from today
        #
        s = StatisticByDate.objects.get(metric=m, date=today)
        assert s.value == 2
