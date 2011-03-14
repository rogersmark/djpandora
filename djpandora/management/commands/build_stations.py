import xmlrpclib

from django.core.management.base import NoArgsCommand
from django.conf import settings

from djpandora import models, utils

class Command(NoArgsCommand):
    """
    Calls to the Pandora XMLRPC Server and builds out our station list
    """

    def handle_noargs(self, **options):
        s = utils.get_pandora_rpc_conn()
        stations = s.get_stations()
        for (id, station_name) in stations.items():
            obj, created = models.Station.objects.get_or_create(
                name=station_name, pandora_id=id
            )
            if not obj.account:
                obj.account = settings.PANDORA_USER
                obj.save()