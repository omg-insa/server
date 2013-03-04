from django.conf.urls.defaults import *

handler500 = 'djangotoolbox.errorviews.server_error'

urlpatterns = patterns('',
  (r'^login/$', 'api.views.login'),
  (r'^register/$', 'api.views.register'),
  (r'^get_user_info/$', 'api.views.getUserInfo'),
  (r'^get_full_user_info/$', 'api.views.getFullUserInfo'),
  (r'^update_user_info/$', 'api.views.updateUserInfo'),
  (r'^get_secret_question/$', 'api.views.getSecretQuestion'),
  (r'^update_secret_question/$', 'api.views.updateSecretQuestion'),
  (r'^update_password/$', 'api.views.updatePassword'),
  (r'^check_completion_status/$', 'api.views.checkProfileCompletion'),
  (r'^get_secret_question_for_recovery/$', 'api.views.getSecretQuestionForRecovery'),
  (r'^check_secret_answer/$', 'api.views.getRecoveryTempToken'),
  (r'^update_password_after_recovery/$', 'api.views.updatePasswordAfterRecovery'),
  (r'^get_places/$', 'api.views.getPlaces'),
  (r'^get_intrests/$', 'api.views.getIntrestsList'),
  (r'^update_intrests/$', 'api.views.updateUserIntrest'),
  (r'^add_intrests/$', 'api.views.addIntrest'),
  (r'^add_message/$', 'api.views.addChatRoomMessage'),
  (r'^add_event/$', 'api.views.addEvent'),
  (r'^get_messages/$', 'api.views.getChatRoomMessage'),


)
