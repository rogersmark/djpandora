from django.core.management.base import NoArgsCommand
from django.conf import settings

from djpandora import models, utils

import pypandora

class Command(NoArgsCommand):
    """
    Starts our Pandora XMLRPC Server
    """

    def handle_noargs(self, **options):
        pypandora.serve()