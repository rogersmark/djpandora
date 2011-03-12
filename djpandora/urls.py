from django.conf.urls.defaults import patterns

urlpatterns = patterns('djpandora.views',
    (r'^$', 'djpandora_index', None, 'djpandora_index'),

)