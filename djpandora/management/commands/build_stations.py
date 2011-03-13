import xmlrpclib

from django.core.management.base import NoArgsCommand
from django.conf import settings

from djpandora import models

class Command(NoArgsCommand):
    """
    Calls to the Pandora XMLRPC Server and builds out our station list
    """

    def handle_noargs(self, **options):
        try:
            host = settings.PANDORA_RPC_HOST
        except AttributeError:
            host = 'localhost'
        try:
            port = settings.PANDORA_RPC_PORT
        except AttributeError:
            port = '8123'
        s = xmlrpclib.ServerProxy('http://%s:%s' % (host, port))
        s.login(settings.PANDORA_USER, settings.PANDORA_PASS); 
        stations = s.get_stations()
        for (id, station_name) in stations.items():
            obj, created = models.Station.objects.get_or_create(
                name=station_name, pandora_id=id
            )