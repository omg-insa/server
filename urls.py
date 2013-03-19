from django.conf.urls.defaults import *

handler500 = 'djangotoolbox.errorviews.server_error'

urlpatterns = patterns('',
    ('^_ah/warmup$', 'djangoappengine.views.warmup'),
    (r'^api/*',include('api.urls')),
    ('^$', 'django.views.generic.simple.direct_to_template',
     {'template': 'index.html'}),
    (r'^download/(?P<path>.*)$', 'django.views.static.serve',
     {'document_root': '/download'}),
)
