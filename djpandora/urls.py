from django.conf.urls.defaults import patterns

urlpatterns = patterns('djpandora.views',
    (r'^$', 'djpandora_index', None, 'djpandora_index'),
    (r'^vote/$', 'djpandora_vote', None, 'djpandora_vote'),
    (r'^pandora_status/$', 'djpandora_status', None, 'djpandora_status'),
    (r'^pandora_stations/$', 'djpandora_stations', None, 'djpandora_stations'),
    (r'^start_station_vote/$', 'start_station_vote', None, 'start_station_vote'),
    (r'^station_vote/$', 'station_vote', None, 'station_vote'),
)