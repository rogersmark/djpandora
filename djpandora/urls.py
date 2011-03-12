from django.conf.urls.defaults import patterns

urlpatterns = patterns('djpandora.views',
    (r'^$', 'djpandora_index', None, 'djpandora_index'),
    (r'^vote/$', 'djpandora_vote', None, 'djpandora_vote'),
    (r'^pandora_status/$', 'djpandora_status', None, 'djpandora_status'),
)