from django.http import HttpResponseForbidden
from api import models
import datetime

__author__ = 'schitic'

def is_logged_in(func):
  """Function decorator for checking the logged in status"""
  def decorator(request, *args, **kwargs):
    token = request.POST.get('auth_token',None)
    if not token:
      return HttpResponseForbidden()
    try:
      auth_info = models.TokenAuthModel.objects.filter(token=token).get()
      if auth_info.expiring_date < datetime.datetime.now() + datetime.timedelta(days=7):
        auth_info.expiring_date = datetime.datetime.now()
        auth_info.save()
        return func(request,*args, **kwargs)
      return HttpResponseForbidden()
    except models.TokenAuthModel.DoesNotExist:
      return HttpResponseForbidden()

  return decorator
