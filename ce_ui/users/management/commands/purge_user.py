import logging
import sys

from django.contrib.auth import get_user_model
from django.core.management.base import BaseCommand
from django.db.models import Q
from topobank.analysis.models import WorkflowResult
from topobank.manager.models import Surface, Topography

_log = logging.getLogger(__name__)


class Command(BaseCommand):
    help = "Deletes a user, the datasets they created, the measurements in " + \
           "those datasets and the analyses of both. Anything else the user " + \
           "touched -- accepted terms, permissions granted to them on other " + \
           "people's datasets -- is left behind. Handle with care."

    def add_arguments(self, parser):
        parser.add_argument('username', type=str)

    def handle(self, *args, **options):
        User = get_user_model()

        try:
            user = User.objects.get(username=options['username'])
        except User.DoesNotExist:
            self.stdout.write(self.style.ERROR(
                "User '{}' does not exist.".format(options['username'])))
            sys.exit(1)

        surfaces = Surface.objects.filter(created_by=user)
        topographies = Topography.objects.filter(surface__in=surfaces)
        analyses = WorkflowResult.objects.filter(
            Q(subject_topography__in=topographies) | Q(subject_surface__in=surfaces)
        )

        _log.info("Removing analyses related to surfaces created by user '{}'..".format(user.name))
        analyses.delete()

        _log.info("Removing topographies related to surfaces created by user '{}'..".format(user.name))
        topographies.delete()

        _log.info("Removing surfaces created by user '{}'..".format(user.name))
        surfaces.delete()

        _log.info("Deleting user object..")
        user.delete()

        self.stdout.write(self.style.SUCCESS(
            "Removed user '{}' and everything related.".format(options['username'])))
        _log.info("Done.")
