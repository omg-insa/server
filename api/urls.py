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
  (r'^get_events/$', 'api.views.getEvents'),
  (r'^get_intrests/$', 'api.views.getIntrestsList'),
  (r'^update_intrests/$', 'api.views.updateUserIntrest'),
  (r'^add_intrests/$', 'api.views.addIntrest'),
  (r'^add_message/$', 'api.views.addChatRoomMessage'),
  (r'^get_messages/$', 'api.views.getChatRoomMessage'),
  (r'^get_current_address/$', 'api.views.getCurrentAddress'),
  (r'^add_local_place/$', 'api.views.addLocalPlace'),
  (r'^get_local_place/$', 'api.views.getLocalPlaceInfo'),
  (r'^add_event_info/$', 'api.views.saveEventInfo'),
  (r'^get_event_info/$', 'api.views.getEventInfo'),
  (r'^save_event_place/$', 'api.views.saveEventPlace'),
  (r'^get_personal_events/$', 'api.views.getPersonalEvents'),
  (r'^save_event_intrest/$', 'api.views.saveEventIntrests'),
  (r'^get_event_intrest/$', 'api.views.getEventIntrests'),
  (r'^close_event/$', 'api.views.closeEvent'),
  (r'^delete_event/$', 'api.views.deleteEvent'),
  (r'^get_event_status/$', 'api.views.getStatus'),
  (r'^checkin/$', 'api.views.checkin'),
  (r'^checkout/$', 'api.views.checkin'),
  (r'^star/$', 'api.views.star'),
  (r'^get_event_full_info/$', 'api.views.getFullEventInfo'),

)
