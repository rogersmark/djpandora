import xmlrpclib

from django.core.management.base import NoArgsCommand
from django.core.exceptions import ObjectDoesNotExist
from django.conf import settings

from djpandora import models, utils

import pypandora

class Command(NoArgsCommand):
    """
    Starts our Pandora XMLRPC Server
    """

    def handle_noargs(self, **options):
        s = xmlrpclib.ServerProxy('http://localhost:8123')
        s.login(settings.PANDORA_USER, settings.PANDORA_PASS)
        try:
            station = models.Station.objects.get(current=True)
            s.play_station(station.pandora_id)
            s.set_volume(0.5)
        except ObjectDoesNotExist:
            stations = models.Station.objects.all().order_by('?')
            if not stations:
                print "No stations"
                return
            station = stations[0]
            station.current = True
            station.save()
            s.play_station(station.pandora_id)