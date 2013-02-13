from django.conf.urls.defaults import *

handler500 = 'djangotoolbox.errorviews.server_error'

urlpatterns = patterns('',
  (r'^login/$', 'api.views.login'),
  (r'^register/$', 'api.views.register'),
  (r'^get_user_info/$', 'api.views.getUserInfo'),
  (r'^get_full_user_info/$', 'api.views.getFullUserInfo'),
)
