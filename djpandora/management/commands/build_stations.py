import xmlrpclib
import logging

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
        pandora_ids = []
        for (id, station_name) in stations.items():
            obj, created = models.Station.objects.get_or_create(
                name=station_name, pandora_id=id, account=settings.PANDORA_USER
            )
            pandora_ids.append(id)

        stations = models.Station.objects.filter(account=settings.PANDORA_USER)
        for station in stations:
            if station.pandora_id not in pandora_ids:
                logging.info("Removed station: %s" % station)
                station.delete()

        