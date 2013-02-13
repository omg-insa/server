# Create your views here.

from django.http import HttpResponse
from django.http import HttpResponseNotAllowed,HttpResponseBadRequest,HttpResponseForbidden
from django.utils import simplejson
from django.contrib.auth.models import User
from api import models
from api import utils
from api import permissions
import datetime
import logging


def login(request):
  """Login request"""
  if request.method == 'POST':
    username = request.POST.get('username', None)
    password = request.POST.get('password', None)
    device_type = request.POST.get('device_type', None)
    device_manufacture = request.POST.get('device_manufacture', None)
    device_os = request.POST.get('device_os', None)
    os_version = request.POST.get('os_version', None)
    device_id = request.POST.get('device_id', None)
    logging.info('Login request from user %s', username)
    logging.info('device_type %s', device_type)
    logging.info('device_manufacture %s', device_manufacture)
    logging.info('device_os  %s', device_os)
    logging.info('os_version %s', os_version)
    logging.info('device_id %s', device_id)

    if not username or not password or not device_id or not device_type or not device_manufacture or not device_manufacture or not device_os or not os_version:
      return HttpResponseBadRequest(simplejson.dumps({'error':'Incomplete data'}))
    try:
      user = User.objects.get(username=username)
      if not user.check_password(password):
        return HttpResponseBadRequest(simplejson.dumps({'error':'Username and password not matching'}))
    except User.DoesNotExist:
      return HttpResponseBadRequest(simplejson.dumps({'error':'Username and password not matching'}))
    try:
      device_info = models.DeviceInfo.objects.filter(device_id=device_id).get()
    except models.DeviceInfo.DoesNotExist:
      device_info = models.DeviceInfo(device_id=device_id, device_manufacture=device_manufacture, device_os=device_os,
        device_type=device_type, os_version=os_version, device_owner=user)
      device_info.save()
     #Generate token and save it
    auth_string = utils.tokenGenerator(size=16)
    while models.TokenAuthModel.objects.filter(token=auth_string).count():
      auth_string = utils.tokenGenerator(size=16)
    expire_date = datetime.datetime.now()
    try:
      auth_token = models.TokenAuthModel.objects.filter(user=user, device=device_info).get()
      auth_token.expiring_date = expire_date
      auth_token.token = auth_string
      auth_token.save()
    except models.TokenAuthModel.DoesNotExist:
      auth_token = models.TokenAuthModel(user=user, device=device_info, token=auth_string,
        expiring_date=expire_date)
      auth_token.save()
    return HttpResponse(simplejson.dumps({'auth_token': auth_string}))
  return HttpResponseNotAllowed(['GET'])


def register(request):
  if request.method == 'POST':
    username =  request.POST.get('username', None)
    email =  request.POST.get('email', None)
    password = request.POST.get('password', None)
    logging.info('User %s is trying to register with email %', username, email)
    if not email or not password or not password:
      return HttpResponseBadRequest(simplejson.dumps({'error':"Incomplete data"}))
    if not utils.validateEmail(email):
      return HttpResponseBadRequest(simplejson.dumps({'error':"Invalid email"}))
    if len(password) < 5:
      return HttpResponseBadRequest(simplejson.dumps({'error':"Password too short"}))
    users = User.objects.filter(email=email)
    if users.count():
      return HttpResponseBadRequest(simplejson.dumps({'error':"Email already used"}))
    users = User.objects.filter(username=username)
    if users.count():
      return HttpResponseBadRequest(simplejson.dumps({'error':"User already registered"}))
    new_user=User.objects.create_user(username,email,password)
    new_user.save()
    return HttpResponse()
  return HttpResponseNotAllowed(['GET'])



