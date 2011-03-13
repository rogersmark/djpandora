import xmlrpclib

from django.conf import settings

def get_pandora_rpc_conn():
    try:
        host = settings.PANDORA_RPC_HOST
    except AttributeError:
        host = 'localhost'
    try:
        port = settings.PANDORA_RPC_PORT
    except AttributeError:
        port = '8123'
    s = xmlrpclib.ServerProxy('http://%s:%s' % (host, port))
    s.login(settings.PANDORA_USER, settings.PANDORA_PASS)
    return s