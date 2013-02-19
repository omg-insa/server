# Create your views here.

from django.http import HttpResponse
from django.http import HttpResponseNotAllowed, HttpResponseBadRequest, HttpResponseForbidden
from django.utils import simplejson
from django.contrib.auth.models import User
from api import models
from api import utils
from api import permissions
import datetime
import logging
import urllib2


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
    logging.info('device_os %s', device_os)
    logging.info('os_version %s', os_version)
    logging.info('device_id %s', device_id)

    if not username or not password or not device_id or not device_type  or not device_os or not os_version:
      return HttpResponseBadRequest(simplejson.dumps({'error': 'Incomplete data'}))
    try:
      user = User.objects.get(username=username)
      if not user.check_password(password):
        return HttpResponseBadRequest(simplejson.dumps({'error': 'Username and password not matching'}))
    except User.DoesNotExist:
      return HttpResponseBadRequest(simplejson.dumps({'error': 'Username and password not matching'}))
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
      auth_token = models.TokenAuthModel.objects.filter(device=device_info).get()
      auth_token.expiring_date = expire_date
      auth_token.token = auth_string
      auth_token.user = user
      device_info.device_owner = user
      device_info.save()
      auth_token.save()
    except models.TokenAuthModel.DoesNotExist:
      auth_token = models.TokenAuthModel(user=user, device=device_info, token=auth_string,
        expiring_date=expire_date)
      auth_token.save()
    return HttpResponse(simplejson.dumps({'auth_token': auth_string}))
  return HttpResponseNotAllowed(['GET'])

def register(request):
  if request.method == 'POST':
    username = request.POST.get('username', None)
    email = request.POST.get('email', None)
    password = request.POST.get('password', None)
    logging.info('User %s is trying to register with email %s', username, email)
    if not email or not password:
      return HttpResponseBadRequest(simplejson.dumps({'error': 'Incomplete data'}))
    if not utils.validateEmail(email):
      return HttpResponseBadRequest(simplejson.dumps({'error': 'Invalid email'}))
    if len(password) < 4:
      return HttpResponseBadRequest(simplejson.dumps({'error': 'Password too short'}))
    users = User.objects.filter(email=email)
    if users.count():
      return HttpResponseBadRequest(simplejson.dumps({'error': 'Email already used'}))
    users = User.objects.filter(username=username)
    if users.count():
      return HttpResponseBadRequest(simplejson.dumps({'error': 'User already registered'}))
    new_user=User.objects.create_user(username, email, password)
    new_user.save()
    return HttpResponse(simplejson.dumps({'empty':'empty'}))
  return HttpResponseNotAllowed(['GET'])

@permissions.is_logged_in
def getUserInfo(request):
  if request.method == 'POST':
    token = request.POST.get('auth_token', None)
    auth_token = models.TokenAuthModel.objects.filter(token=token).get()
    user = auth_token.user
    return HttpResponse(simplejson.dumps({'email': user.email, 'full_name': user.first_name, 'username': user.username}))
  return HttpResponseNotAllowed(['GET'])

@permissions.is_logged_in
def getFullUserInfo(request):
  if request.method == 'POST':
    token = request.POST.get('auth_token', None)
    auth_token = models.TokenAuthModel.objects.filter(token=token).get()
    user = auth_token.user
    try:
      personalInfo = models.ExtraInfoForUser.objects.filter(user=user).get()
    except models.ExtraInfoForUser.DoesNotExist:
      personalInfo = models.ExtraInfoForUser(user=user)
      personalInfo.save()
    dictToReturn = {'first_name': user.first_name, 'email': user.email, 'birthday': personalInfo.birthday, 'sex': personalInfo.sex, 'username': user.username}
    return HttpResponse(simplejson.dumps(dictToReturn))
  return HttpResponseNotAllowed(['GET'])

@permissions.is_logged_in
def updateUserInfo(request):
  if request.method == 'POST':
    token = request.POST.get('auth_token', None)
    first_name = request.POST.get('full_name', None)
    email = request.POST.get('email', None)
    birthday = request.POST.get('birthday', None)
    sex = request.POST.get('sex', None)
    auth_token = models.TokenAuthModel.objects.filter(token=token).get()
    user = auth_token.user
    users = User.objects.filter(email=email)
    if first_name is None or email is None or birthday is None or sex is None:
      return HttpResponseBadRequest(simplejson.dumps({'error': 'Incomplete data'}))
    if not utils.validateEmail(email):
      return HttpResponseBadRequest(simplejson.dumps({'error': 'Invalid email'}))
    if (users.count() == 1 and users.get() != user) or users.count()>1:
      return HttpResponseBadRequest(simplejson.dumps({'error': 'Email already used'}))
    try:
      personalInfo = models.ExtraInfoForUser.objects.filter(user=user).get()
    except modesl.ExtraInfoForUser.DoesNotExist:
      personalInfo = models.ExtraInfoForUser(user=user, sex=sex, birthday=birthday)
      personalInfo.save()
    user.first_name = first_name
    personalInfo.sex = sex
    personalInfo.birthday = birthday
    personalInfo.save()
    user.email = email
    user.save()
    return HttpResponse(simplejson.dumps({'empty':'empty'})) 
  return HttpResponseNotAllowed(['GET'])

@permissions.is_logged_in
def getSecretQuestion(request):
  if request.method == 'POST':
    token = request.POST.get('auth_token', None)
    auth_token = models.TokenAuthModel.objects.filter(token=token).get()
    user = auth_token.user
    try:
      personalInfo = models.ExtraInfoForUser.objects.filter(user=user).get()
    except models.ExtraInfoForUser.DoesNotExist:
      personalInfo = models.ExtraInfoForUser(user=user)
      personalInfo.save()
    dictToReturn = {'secret_question': personalInfo.secret_question}
    return HttpResponse(simplejson.dumps(dictToReturn))
  return HttpResponseNotAllowed(['GET'])

@permissions.is_logged_in
def updateSecretQuestion(request):
  if request.method == 'POST':
    token = request.POST.get('auth_token', None)
    secret_question = request.POST.get('secret_question', None)
    secret_answer = request.POST.get('secret_answer', None)
    password = request.POST.get('password', None)
    auth_token = models.TokenAuthModel.objects.filter(token=token).get()
    user = auth_token.user
    if secret_question is None or secret_answer is None or password is None:
      return HttpResponseBadRequest(simplejson.dumps({'error': 'Incomplete data'}))
    if not user.check_password(password):
      return HttpResponseBadRequest(simplejson.dumps({'error': 'Wrong password'}))
    try:
      personalInfo = models.ExtraInfoForUser.objects.filter(user=user).get()
    except models.ExtraInfoForUser.DoesNotExist:
      personalInfo = models.ExtraInfoForUser(user=user)
      personalInfo.save()
    personalInfo.secret_question = secret_question
    personalInfo.secret_answer = secret_answer
    personalInfo.save()
    return HttpResponse(simplejson.dumps({'empty':'empty'})) 
  return HttpResponseNotAllowed(['GET'])

@permissions.is_logged_in
def updatePassword(request):
  if request.method == 'POST':
    token = request.POST.get('auth_token', None)
    new_password = request.POST.get('new_password', None)
    password = request.POST.get('password', None)
    if password is None or new_password is None:
      return HttpResponseBadRequest(simplejson.dumps({'error': 'Incomplete data'}))
    auth_token = models.TokenAuthModel.objects.filter(token=token).get()
    user = auth_token.user
    if not user.check_password(password):
      return HttpResponseBadRequest(simplejson.dumps({'error': 'Wrong password'}))
    user.set_password(new_password)
    user.save()
    return HttpResponse(simplejson.dumps({'empty':'empty'})) 
  return HttpResponseNotAllowed(['GET'])

@permissions.is_logged_in
def checkProfileCompletion(request):
  if request.method == 'POST':
    token = request.POST.get('auth_token', None)
    auth_token = models.TokenAuthModel.objects.filter(token=token).get()
    try:
      extra_info = models.ExtraInfoForUser.objects.filter(user=auth_token.user).get()
    except models.ExtraInfoForUser.DoesNotExist:
      return HttpResponseBadRequest(simplejson.dumps({'error': 'No data'}))
    if extra_info.secret_question == '' or extra_info.secret_answer == ''  or extra_info.birthday == '' or extra_info.sex == '':
      return HttpResponseBadRequest(simplejson.dumps({'error': 'No data'}))
    return HttpResponse(simplejson.dumps({'empty':'empty'})) 
  return HttpResponseNotAllowed(['GET'])


def getSecretQuestionForRecovery(request):
  if request.method == 'POST':
    username =  request.POST.get('username', None)
    if username is None:
      return HttpResponseBadRequest(simplejson.dumps({'error': 'Incomplete data'}))
    try:
      user = User.objects.filter(username=username).get()
    except User.DoesNotExist:
      return HttpResponseBadRequest(simplejson.dumps({'error': 'User does not exists'}))
    try:
      user_extra = models.ExtraInfoForUser.objects.filter(user=user).get()
    except models.ExtraInfoForUser.DoesNotExist:
      return HttpResponseBadRequest(simplejson.dumps({'error': 'User does not have security questions'}))
    if user_extra.secret_answer == '' or user_extra.secret_question == '' or user_extra.birthday == '':
      return HttpResponseBadRequest(simplejson.dumps({'error': 'User does not have security questions'}))
    return HttpResponse(simplejson.dumps({'secret_question': user_extra.secret_question}))
  return HttpResponseNotAllowed(['GET'])


def getRecoveryTempToken(request):
  if request.method == 'POST':
    username =  request.POST.get('username', None)
    answer =  request.POST.get('answer', None)
    birthday =  request.POST.get('birthday', None)
    if username is None or  answer is None or birthday is None:
      return HttpResponseBadRequest(simplejson.dumps({'error': 'Incomplete data'}))
    try:
      user = User.objects.filter(username=username).get()
    except User.DoesNotExist:
      return HttpResponseBadRequest(simplejson.dumps({'error': 'User dose not exists'}))
    try:
      user_extra = models.ExtraInfoForUser.objects.filter(user=user).get()
    except models.ExtraInfoForUser.DoesNotExist:
      return HttpResponseBadRequest(simplejson.dumps({'error': 'User dose not have security questions'}))
    if user_extra.secret_answer == '' or user_extra.secret_question == '' or user_extra.birthday == '':
      return HttpResponseBadRequest(simplejson.dumps({'error': 'User dose not have security questions'}))
    if user_extra.secret_answer != answer or user_extra.birthday != birthday:
      return HttpResponseBadRequest(simplejson.dumps({'error': 'Wrong answer'}))
    tmp_token = utils.tokenGenerator(size=10)
    revoery_model = models.RecoveryTokens(token=tmp_token, user=user, expiringDate = datetime.datetime.now() + datetime.timedelta(seconds=30))
    revoery_model.save()
    return HttpResponse(simplejson.dumps({'tmp_token': tmp_token}))
  return HttpResponseNotAllowed(['GET'])


def updatePasswordAfterRecovery(request):
  if request.method == 'POST':
    token =  request.POST.get('tmp_token', None)
    new_password = request.POST.get('new_password', None)
    username =  request.POST.get('user', None)
    if token is None or new_password is None or username is None:
      return HttpResponseBadRequest(simplejson.dumps({'error': 'Incomplete data'}))
    try:
      user =  User.objects.filter(username=username).get()
      tmp_auth = models.RecoveryTokens.objects.filter(token=token, user=user).get()
      if tmp_auth:
        user.set_password(new_password)
        user.save()
    except (models.RecoveryTokens.DoesNotExist, User.DoesNotExist):
      return HttpResponseBadRequest(simplejson.dumps({'error': 'Wrong data'}))
    return HttpResponse(simplejson.dumps({'empty':'empty'})) 

@permissions.is_logged_in
def getPlaces(request):
  if request.method == 'POST':
    radius = request.POST.get('radius', None)
    latitude = request.POST.get('latitude', None)
    longitude = request.POST.get('longitude', None)
    """TODO: get from cache if possible"""
    """TODO: put things into cache"""
    json = urllib2.urlopen('https: //maps.googleapis.com/maps/api/place/search/json?location=' + latitude + ',' + longitude + '&radius=' + radius + '&types=bar|night_club&name=&sensor=false&key=AIzaSyDH-hG0w9pGBjGFBcpoNb25EDaG4P11zPI').read()
    return HttpResponse(json)
  return HttpResponseNotAllowed(['GET'])
