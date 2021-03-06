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
import math

__PlacesKey__ = 'AIzaSyBLHdzA-5F9DCllQbLmataclCyVp8MSXok'

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
    return HttpResponse(simplejson.dumps({'empty': 'empty'}))
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
    dictToReturn = {'full_name': user.first_name, 'email': user.email, 'birthday': personalInfo.birthday, 'sex': personalInfo.sex, 'status': personalInfo.status, 'username': user.username}
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
    status = request.POST.get('status', None)
    auth_token = models.TokenAuthModel.objects.filter(token=token).get()
    user = auth_token.user
    users = User.objects.filter(email=email)
    if first_name is None or email is None or birthday is None or sex is None or status is None:
      return HttpResponseBadRequest(simplejson.dumps({'error': 'Incomplete data'}))
    if not utils.validateEmail(email):
      return HttpResponseBadRequest(simplejson.dumps({'error': 'Invalid email'}))
    if (users.count() == 1 and users.get() != user) or users.count() > 1:
      return HttpResponseBadRequest(simplejson.dumps({'error': 'Email already used'}))
    try:
      personalInfo = models.ExtraInfoForUser.objects.filter(user=user).get()
    except modesl.ExtraInfoForUser.DoesNotExist:
      personalInfo = models.ExtraInfoForUser(user=user, sex=sex, birthday=birthday, status=status)
      personalInfo.save()
    user.first_name = first_name
    personalInfo.status = status
    personalInfo.sex = sex
    personalInfo.birthday = birthday
    personalInfo.save()
    user.email = email
    user.save()
    return HttpResponse(simplejson.dumps({'empty': 'empty'}))
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
    dictToReturn = {'secret_question': personalInfo.secret_question, 'secret_answer': personalInfo.secret_answer}
    return HttpResponse(simplejson.dumps(dictToReturn))
  return HttpResponseNotAllowed(['GET'])

@permissions.is_logged_in
def updateSecretQuestion(request):
  if request.method == 'POST':
    token = request.POST.get('auth_token', None)
    secret_question = request.POST.get('secret_question', None)
    secret_answer = request.POST.get('secret_answer', None)
    password = request.POST.get('password', None)
    logging.error('%s', request.POST)
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
    return HttpResponse(simplejson.dumps({'empty': 'empty'}))
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
    return HttpResponse(simplejson.dumps({'empty': 'empty'}))
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
    return HttpResponse(simplejson.dumps({'empty': 'empty'}))
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
    return HttpResponse(simplejson.dumps({'empty': 'empty'}))

def _getPlaceDetails(place_id):
  if not place_id:
    return None
  url = 'https://maps.googleapis.com/maps/api/place/details/json?reference=' + place_id + '&sensor=false&key='+__PlacesKey__
  json = urllib2.urlopen(url).read()
  data = simplejson.loads(json)
  return data['result']

@permissions.is_logged_in
def getPlaces(request):
  if request.method == 'POST':
    places = _getPlaces(request)
    return HttpResponse(simplejson.dumps({'list': places}))
  return HttpResponseNotAllowed(['GET'])

def _getPlaces(request):
  radius = request.POST.get('radius', None)
  latitude = request.POST.get('latitude', None)
  longitude = request.POST.get('longitude', None)
  if not radius or not latitude or not longitude:
    return None
  logging.info("Lon %s, Lat %s, Radious %s",longitude,latitude,radius)
  url = 'https://maps.googleapis.com/maps/api/place/search/json?location=' + latitude + ',' + longitude + '&radius=' + radius + '&types=bar|night_club&name=&sensor=false&key='+ __PlacesKey__
  json = urllib2.urlopen(url).read()
  data = simplejson.loads(json)
  logging.info("Google Places: %s",data)
  to_return = []
  for d in data['results']:
    to_return.append({'id': d['id'],'reference':d['reference'], 'image_url': d['icon'], 'source': 'False', 'type': d['types'][0], 'name': d['name'], 'description': '', 'address': d['vicinity'], 'lon': d['geometry']['location']['lng'], 'lat': d['geometry']['location']['lat']})
  R=6378137.0
  radius = (float)(radius) * 1.0
  dLat = radius/R
  lon_coef = math.pi*((float)(latitude))/180.0
  lon_coef = math.cos(lon_coef)
  dLon = radius/(R*lon_coef)
  logging.info("%s %s",dLat,dLon)
  lat_range = (float(latitude)-dLat * 180/math.pi, float(latitude)+dLat * 180/math.pi)
  lon_range = (float(longitude)-dLon * 180/math.pi, float(longitude)+dLon * 180/math.pi)
  local_places = models.LocalPlaces.objects.filter(lat__range=lat_range)
  for obj in local_places:
    if float(obj.lon) >= lon_range[0] and float(obj.lon) <= lon_range[1]:
      to_return.append({'id': obj.id, 'reference':obj.id,'image_url': 'http://naperville-webdesign.net/wp-content/uploads/2012/12/home-icon-hi.png', 'source': 'True', 'type': obj.type, 'name': obj.name, 'description': obj.description, 'address': obj.address, 'lon': obj.lon, 'lat': obj.lat})
  return to_return

@permissions.is_logged_in
def getEvents(request):
  if request.method == 'POST':
    places = _getPlaces(request)
    intrest = request.POST.get('intrest', None)
    prix = request.POST.get('prix', None)
    time = request.POST.get('time', None)
    logging.info("Get data: %s, %s %s",intrest,prix,time)
    to_return = []
    intrests_id = []
    if intrest:
      token = request.POST.get('auth_token',None)
      auth_token = models.TokenAuthModel.objects.filter(token=token).get()
      user = auth_token.user
      intrests = models.UserIntrest.objects.filter(user = user)
      if intrests.count():
        for e in intrests:
          intrests_id.append(e.intrest.id)
    logging.info("Look for intrests: %s", intrests_id)
    for place in places:
      if place['source'] != "False":
        events = models.Event.objects.filter(place_id=place['id']).all()
      else:
        events = models.Event.objects.filter(place_id=place['id']).all()
      logging.info("Events Count : %d %s", events.count(),place['id'])
      for event in events:
        if event.status == "Closed":
          logging.info("Exited because event is closed")
          continue
        if prix  and (int)(event.price) > (int)(prix):
          logging.info("Exited because of the price %s %s", prix, event.price)
          continue
        if time and  event.start_time < time:
          logging.info("Exited because of the time %s %s", time,event.start_time)
          continue
        if len(intrests_id):
          event_intrests = models.EventIntrests.objects.filter(event = event)
          ok = False
          for e in event_intrests:
            logging.info("Found intrests: %s", e.intrest.id)
            if e.intrest.id in intrests_id:
              ok = True
          if not ok:
            continue
        currentDate = datetime.datetime.now()
        timeDelta = event.date.day - currentDate.day
        if timeDelta > 1 or timeDelta < -1:
          logging.info("Exited because event has not the good date")
          continue
        try:
          if event.local != "False":
            if not event.place_id:
              lon=lat=0
            else:
              place_tmp = models.LocalPlaces.objects.filter(id=event.place_id).get()
              lon = place_tmp.lon
              lat = place_tmp.lat
          else:
            if not event.place_id:
              lon=lat=0
            else:
              logging.info('Place id %s:', event.place_id)
              place_tmp = _getPlaceDetails(event.reference)
              logging.info('data :%s',place)
              lon = place_tmp['geometry']['location']['lng']
              lat = place_tmp['geometry']['location']['lat']
        except models.LocalPlaces.DoesNotExist:
          lon = lat = 0;
        if lon > 0 and lat > 0:
          to_return.append({'id': event.id, 'name': event.name,'address':_convertToAddress(lon,lat), 'description': event.description, 'start_time': event.start_time, 'end_time': event.end_time, 'type': place['type'],'lon': lon, 'lat': lat})
    return HttpResponse(simplejson.dumps({'list': to_return}))
  return HttpResponseNotAllowed(['GET'])

@permissions.is_logged_in
def getIntrestsList(request):
  if request.method == 'POST':
    token = request.POST.get('auth_token', None)
    auth_token = models.TokenAuthModel.objects.filter(token=token).get()
    user = auth_token.user
    intrests = models.Intrests.objects.all()
    toReturn = []
    for i in intrests:
      isSelected = False
      if models.UserIntrest.objects.filter(user=user, intrest=i).count():
        isSelected = True
      toReturn.append({'name': i.name, 'description': i.description, 'selected': isSelected, 'id': i.id})
    return HttpResponse(simplejson.dumps({'list': toReturn}))
  return HttpResponseNotAllowed(['GET'])

@permissions.is_logged_in
def updateUserIntrest(request):
  if request.method == 'POST':
    token = request.POST.get('auth_token', None)
    intrest = request.POST.get('intrest', None)
    if intrest is None:
      return HttpResponseBadRequest(simplejson.dumps({'error': 'Incomplete data'}))
    auth_token = models.TokenAuthModel.objects.filter(token=token).get()
    user = auth_token.user
    try:
      intrest_model = models.Intrests.objects.filter(id=intrest).get()
    except models.Intrests.DoesNotExist:
      return HttpResponseBadRequest(simplejson.dumps({'error': 'Intrest dose not exist'}))
    try:
      user_intrest = models.UserIntrest.objects.filter(user=user, intrest=intrest_model).get()
      user_intrest.delete()
    except models.UserIntrest.DoesNotExist:
      user_intrest = models.UserIntrest(user=user, intrest=intrest_model)
      user_intrest.save()
    return HttpResponse(simplejson.dumps({'empty': 'empty'}))
  return HttpResponseNotAllowed(['GET'])

def addIntrest(request):
  models.Intrests(name=request.GET.get('name', ''), description=request.GET.get('description', '')).save()
  return HttpResponse(simplejson.dumps({'empty': 'empty'}))

@permissions.is_logged_in
def addChatRoomMessage(request):
  if request.method == 'POST':
    token = request.POST.get('auth_token', None)
    message = request.POST.get('message', None)
    event = request.POST.get('event_id', None)
    if message is None or event is None:
      return HttpResponseBadRequest(simplejson.dumps({'error': 'Incomplete data'}))
    auth_token = models.TokenAuthModel.objects.filter(token=token).get()
    try:
      event_models = models.Event.objects.filter(id=event).get()
    except models.Event.DoesNotExist:
      return HttpResponseBadRequest(simplejson.dumps({'error': 'Event dose not exist'}))
    user = auth_token.user
    message_model = models.EventChatRoom(user=user, message=message, event=event_models, date = datetime.datetime.now())
    message_model.save()
    return HttpResponse(simplejson.dumps({'empty': 'empty'}))
  return HttpResponseNotAllowed(['GET'])

@permissions.is_logged_in
def getChatRoomMessage(request):
  if request.method == 'POST':
    event = request.POST.get('event_id', None)
    if event is None:
      return HttpResponseBadRequest(simplejson.dumps({'error': 'Incomplete data'}))
    try:
      event_models = models.Event.objects.filter(id=event).get()
    except models.Event.DoesNotExist:
      return HttpResponseBadRequest(simplejson.dumps({'error': 'Event dose not exist'}))
    messages = models.EventChatRoom.objects.filter(event = event_models).order_by('-date')
    to_return = []
    for msg in messages:
      to_return.append({'date': msg.date.strftime('%d/%m/%y %H:%M:%S'), 'message': msg.message, 'user': msg.user.username})
    return HttpResponse(simplejson.dumps({'list': to_return}))
  return HttpResponseNotAllowed(['GET'])

@permissions.is_logged_in
def getFullEventInfo(request):
  if request.method == 'POST':
    id =  request.POST.get('id', None)
    if id is None:
      return HttpResponseBadRequest(simplejson.dumps({'error': 'Incomplete data'}))
    try:
      event = models.Event.objects.filter(id=id).get()
      try:
        if event.local != "False":
          if not event.place_id:
            lon=lat=0
          else:
            place_tmp = models.LocalPlaces.objects.filter(id=event.place_id).get()
            lon = place_tmp.lon
            lat = place_tmp.lat
            name =  place_tmp.name
            address = place_tmp.address
            type = place_tmp.type
            place_description = place_tmp.description
        else:
          if not event.place_id:
            lon=lat=0
          else:
            logging.info('Place id %s:', event.place_id)
            place_tmp = _getPlaceDetails(event.reference)
            name = place_tmp['name']
            place_description = ''
            lon = place_tmp['geometry']['location']['lng']
            lat = place_tmp['geometry']['location']['lat']
            logging.info("Place details %s",place_tmp)
            address = _convertToAddress(lon,lat)
            type = place_tmp['types'][0]
      except models.LocalPlaces.DoesNotExist:
        lon = lat = 0;
      if lon > 0 and lat > 0:
        myDict = {'name': event.name, 'close': event.status, 'description': event.description, 'price': event.price, 'start_time': event.start_time, 'end_time': event.end_time,
                  'age_average':event.age_average, 'females':event.females, 'stars':event.stars, 'singles':event.singles, 'headcount':event.headcount, 'lon':lon,
                  'lat':lat,'place_name':name,'place_description':place_description,'place_address':address,
                  'type':type}
        return HttpResponse(simplejson.dumps(myDict))
    except models.LocalPlaces.DoesNotExist:
      return HttpResponseBadRequest(simplejson.dumps({'error': 'Object does not exists'}))
  return HttpResponseNotAllowed(['GET'])

@permissions.is_logged_in
def getEventInfo(request):
  if request.method == 'POST':
    id =  request.POST.get('id', None)
    token = request.POST.get('auth_token', None)
    auth_token = models.TokenAuthModel.objects.filter(token=token).get()
    if not id:
      return HttpResponseBadRequest(simplejson.dumps({'error': 'Incomplete data'}))
    try:
      event = models.Event.objects.filter(id=id).get()
      if event.creator_id != auth_token.user:
        return HttpResponseBadRequest(simplejson.dumps({'error': 'Forbidden to edit'}))
      return HttpResponse(simplejson.dumps({'name': event.name, 'close': event.status, 'description': event.description, 'price': event.price, 'start_time': event.start_time, 'end_time': event.end_time}))
    except models.LocalPlaces.DoesNotExist:
      return HttpResponseBadRequest(simplejson.dumps({'error': 'Object does not exists'}))
  return HttpResponseNotAllowed(['GET'])

@permissions.is_logged_in
def saveEventInfo(request):
  if request.method == 'POST':
    name = request.POST.get('name', None)
    description = request.POST.get('description', None)
    start_time = request.POST.get('start_time', None)
    end_time = request.POST.get('end_time', None)
    price = request.POST.get('price', None)
    id =  request.POST.get('id', None)
    token = request.POST.get('auth_token', None)
    auth_token = models.TokenAuthModel.objects.filter(token=token).get()
    if not name or not description or not start_time or not end_time or not price:
      return HttpResponseBadRequest(simplejson.dumps({'error': 'Incomplete data'}))
    if not id:
      event = models.Event(name=name, description=description,
        date = datetime.datetime.now(),
        start_time=start_time, end_time=end_time, price=price, creator_id=auth_token.user)
      _recompute(event)
      return HttpResponse(simplejson.dumps({'id': event.id}))
    else:
      try:
        event = models.Event.objects.filter(id=id).get()
        event.name = name
        event.description = description
        event.start_time = start_time
        event.date = datetime.datetime.now()
        event.end_time = end_time
        event.price = price
        if event.creator_id != auth_token.user:
          return HttpResponseBadRequest(simplejson.dumps({'error': 'Forbidden to edit'}))
        _recompute(event)
        return HttpResponse(simplejson.dumps({'id': event.id}))
      except models.LocalPlaces.DoesNotExist:
        return HttpResponseBadRequest(simplejson.dumps({'error': 'Object does not exists'}))
  return HttpResponseNotAllowed(['GET'])

@permissions.is_logged_in
def saveEventPlace(request):
  if request.method == 'POST':
    place_id = request.POST.get('place_id', None)
    place_reference = request.POST.get('place_reference', None)
    event_id = request.POST.get('event_id', None)
    is_local = request.POST.get('is_local', None)
    token = request.POST.get('auth_token', None)
    auth_token = models.TokenAuthModel.objects.filter(token=token).get()
    if not place_id or not event_id or not is_local:
      return HttpResponseBadRequest(simplejson.dumps({'error': 'Incomplete data'}))
    if is_local == "True":
      try:
        place = models.LocalPlaces.objects.filter(id=place_id).get()
      except models.LocalPlaces.DoesNotExist:
        return HttpResponseBadRequest(simplejson.dumps({'error': 'Object does not exists'}))
    try:
      event = models.Event.objects.filter(id=event_id).get()
      if event.creator_id != auth_token.user:
        return HttpResponseBadRequest(simplejson.dumps({'error': 'Forbidden to edit'}))
      event.local = is_local
      if is_local == "True":
        event.place_id = place.id
      else:
        event.place_id = place_id
        event.reference = place_reference
      _recompute(event)
      return HttpResponseBadRequest(simplejson.dumps({'id': event.id}))
    except models.LocalPlaces.DoesNotExist:
      return HttpResponseBadRequest(simplejson.dumps({'error': 'Object does not exists'}))
  return HttpResponseNotAllowed(['GET'])

@permissions.is_logged_in
def getPersonalEvents(request):
  if request.method == 'POST':
    token = request.POST.get('auth_token', None)
    auth_token = models.TokenAuthModel.objects.filter(token=token).get()
    personalEvents = models.Event.objects.filter(creator_id=auth_token.user)
    to_return = []
    for event in personalEvents:
      try:
        if event.local != "False":
          if not event.place_id:
            lon=lat=0
          else:
            place = models.LocalPlaces.objects.filter(id=event.place_id).get()
            lon = place.lon
            lat = place.lat
        else:
          if not event.place_id:
            lon=lat=0
          else:
            logging.info('Place id %s:', event.place_id)
            place = _getPlaceDetails(event.reference)
            logging.info('data :%s',place)
            lon = place['geometry']['location']['lng']
            lat = place['geometry']['location']['lat']
      except models.LocalPlaces.DoesNotExist:
        lon = lat = 0;
      if lon > 0 and lat > 0:
        to_return.append({'id': event.id, 'name': event.name, 'description': event.description, 'start_time': event.start_time, 'end_time': event.end_time, 'lon': lon, 'lat': lat})
    return HttpResponse(simplejson.dumps({'list': to_return}))
  return HttpResponseNotAllowed(['GET'])

def _convertToAddress(lon, lat):
  url = 'http://maps.googleapis.com/maps/api/geocode/json?latlng=%s,%s&sensor=false' % (lat,lon)
  json = urllib2.urlopen(url).read()
  data = simplejson.loads(json)
  logging.info("Address %s", data)
  return data['results'][0]['formatted_address']

@permissions.is_logged_in
def getCurrentAddress(request):
  if request.method == 'POST':
    lon = request.POST.get('longitude', None)
    lat = request.POST.get('latitude', None)
    if not lon or not lat:
      return HttpResponseBadRequest(simplejson.dumps({'error': 'Incomplete data'}))
    return HttpResponse(simplejson.dumps({'address': _convertToAddress(lon, lat)}))
  return HttpResponseNotAllowed(['GET'])

@permissions.is_logged_in
def addLocalPlace(request):
  if request.method == 'POST':
    name = request.POST.get('name', None)
    description = request.POST.get('description', None)
    type = request.POST.get('type', None)
    lon = request.POST.get('longitude', None)
    lat = request.POST.get('latitude', None)
    id =  request.POST.get('id', None)
    if not name or not description or not type or not lon or not lat:
      return HttpResponseBadRequest(simplejson.dumps({'error': 'Incomplete data'}))
    if not id:
      place = models.LocalPlaces(name=name, description=description, lon=lon, lat=lat, type=type, address=_convertToAddress(lon, lat))
      place.save()
      return HttpResponse(simplejson.dumps({'id': place.id}))
    else:
      try:
        place = models.LocalPlaces.objects.filter(id=id).get()
        place.name = name
        place.description = description
        place.type = type
        place.lon = lon
        place.lat = lat
        place.address = _convertToAddress(lon, lat)
        place.save()
        return HttpResponse(simplejson.dumps({'id': place.id}))
      except models.LocalPlaces.DoesNotExist:
        return HttpResponseBadRequest(simplejson.dumps({'error': 'Object does not exists'}))
  return HttpResponseNotAllowed(['GET'])

@permissions.is_logged_in
def getLocalPlaceInfo(request):
  if request.method == 'POST':
    id =  request.POST.get('id', None)
    if not id:
      return HttpResponseBadRequest(simplejson.dumps({'error': 'Incomplete data'}))
    try:
      place = models.LocalPlaces.objects.filter(id=id).get()
      return HttpResponse(simplejson.dumps({'name': place.name, 'description': place.description, 'type': place.type, 'lon': place.lon, 'lat': place.lat, 'address': place.address}))
    except models.LocalPlaces.DoesNotExist:
      return HttpResponseBadRequest(simplejson.dumps({'error': 'Object does not exists'}))
  return HttpResponseNotAllowed(['GET'])

@permissions.is_logged_in
def saveEventIntrests(request):
  if request.method == 'POST':
    event_id = request.POST.get('event_id', None)
    intrest = request.POST.get('intrest_id', None)
    if intrest is None or not event_id:
      return HttpResponseBadRequest(simplejson.dumps({'error': 'Incomplete data'}))
    try:
      intrest_model = models.Intrests.objects.filter(id=intrest).get()
    except models.Intrests.DoesNotExist:
      return HttpResponseBadRequest(simplejson.dumps({'error': 'Intrest dose not exist'}))
    try:
      event_model = models.Event.objects.filter(id=event_id).get()
    except models.Intrests.DoesNotExist:
      return HttpResponseBadRequest(simplejson.dumps({'error': 'Event dose not exist'}))
    try:
      event_intrest = models.EventIntrests.objects.filter(event=event_model, intrest=intrest_model).get()
      event_intrest.delete()
    except models.EventIntrests.DoesNotExist:
      event_intrest = models.EventIntrests(event=event_model, intrest=intrest_model)
      event_intrest.save()
    return HttpResponse(simplejson.dumps({'empty': 'empty'}))
  return HttpResponseNotAllowed(['GET'])

@permissions.is_logged_in
def getEventIntrests(request):
  if request.method == 'POST':
    event_id = request.POST.get('event_id', None)
    if not event_id:
      return HttpResponseBadRequest(simplejson.dumps({'error': 'Incomplete data'}))
    try:
      event_model = models.Event.objects.filter(id=event_id).get()
    except models.Intrests.DoesNotExist:
      return HttpResponseBadRequest(simplejson.dumps({'error': 'Event dose not exist'}))
    intrests = models.Intrests.objects.all()
    toReturn = []
    for i in intrests:
      isSelected = False
      if models.EventIntrests.objects.filter(event=event_model, intrest=i).count():
        isSelected = True
      toReturn.append({'name': i.name, 'description': i.description, 'selected': isSelected, 'id': i.id})
    return HttpResponse(simplejson.dumps({'list': toReturn}))
  return HttpResponseNotAllowed(['GET'])

@permissions.is_logged_in
def closeEvent(request):
  if request.method == 'POST':
    event_id = request.POST.get('event_id', None)
    token = request.POST.get('auth_token', None)
    auth_token = models.TokenAuthModel.objects.filter(token=token).get()
    if not event_id:
      return HttpResponseBadRequest(simplejson.dumps({'error': 'Incomplete data'}))
    try:
      event = models.Event.objects.filter(id=event_id).get()
      if event.creator_id != auth_token.user:
        return HttpResponseBadRequest(simplejson.dumps({'error': 'Forbidden to edit'}))
      if event.status == 'Closed':
        event.status = ''
      else:
        event.status = 'Closed'
      _recompute(event)
      return HttpResponseBadRequest(simplejson.dumps({'id': event.id}))
    except models.LocalPlaces.DoesNotExist:
      return HttpResponseBadRequest(simplejson.dumps({'error': 'Object does not exists'}))
  return HttpResponseNotAllowed(['GET'])

@permissions.is_logged_in
def getStatus(request):
  if request.method == 'POST':
    event_id = request.POST.get('event_id', None)
    if not event_id:
      return HttpResponseBadRequest(simplejson.dumps({'error': 'Incomplete data'}))
    try:
      event = models.Event.objects.filter(id=event_id).get()
      if event.status != "Closed":
        status = "Open"
      else:
        status = event.status
      return HttpResponseBadRequest(simplejson.dumps({'status': status}))
    except models.LocalPlaces.DoesNotExist:
      return HttpResponseBadRequest(simplejson.dumps({'error': 'Object does not exists'}))
  return HttpResponseNotAllowed(['GET'])

@permissions.is_logged_in
def deleteEvent(request):
  if request.method == 'POST':
    event_id = request.POST.get('event_id', None)
    token = request.POST.get('auth_token', None)
    auth_token = models.TokenAuthModel.objects.filter(token=token).get()
    if not event_id:
      return HttpResponseBadRequest(simplejson.dumps({'error': 'Incomplete data'}))
    try:
      event = models.Event.objects.filter(id=event_id).get()
      if event.creator_id != auth_token.user:
        return HttpResponseBadRequest(simplejson.dumps({'error': 'Forbidden to edit'}))
      event.delete()
      return HttpResponseBadRequest(simplejson.dumps({'id': event.id}))
    except models.LocalPlaces.DoesNotExist:
      return HttpResponseBadRequest(simplejson.dumps({'error': 'Object does not exists'}))
  return HttpResponseNotAllowed(['GET'])

@permissions.is_logged_in
def checkin(request):
  if request.method == 'POST':
    token = request.POST.get('auth_token', None)
    user = models.TokenAuthModel.objects.filter(token=token).get().user
    event_id = request.POST.get('event_id', None)
    event = models.Event.objects.filter(id=event_id).get()
    try:
      subscription = models.Subscription.objects.filter(user=user, event=event).get()
    except models.Subscription.DoesNotExist:
      subscription = models.Subscription(user=user, event=event)
      subscription.save()
      _recompute(event)
    return HttpResponse(simplejson.dumps({'empty': 'empty'}))
  return HttpResponseNotAllowed(['GET'])

@permissions.is_logged_in
def checkout(request):
  if request.method == 'POST':
    token = request.POST.get('auth_token', None)
    user = models.TokenAuthModel.objects.filter(token=token).get().user
    event_id = request.POST.get('event_id', None)
    event = models.Event.objects.filter(id=event_id).get()
    subscription = models.Subscription.objects.filter(user=user, event=event).get()
    subscription.delete()
    _recompute(event)
    return HttpResponse(simplejson.dumps({'empty': 'empty'}))
  return HttpResponseNotAllowed(['GET'])

def _recompute(event):
  event.headcount = 0
  event.age_average = 0
  event.females = 0
  event.singles = 0
  unknowns = 0;
  now = datetime.datetime.now()
  for s in models.Subscription.objects.filter(event=event).all():
    try:
      info = models.ExtraInfoForUser.objects.filter(user=s.user).get()
      if (len(info.birthday) != 8):
        continue
      event.headcount += 1
      year = int(info.birthday[:4])
      month = int(info.birthday[4:6])
      day = int(info.birthday[6:8])
      event.age_average += now.year - year - (now.month < month or ( now.month == month and now.day < day ) )
      event.females += info.sex == "2"
      event.singles += info.status == "2"
    except models.ExtraInfoForUser.DoesNotExist:
      logging.info('Extra info dose not exists')
      unknowns += 1
  if (event.headcount > 0):
    event.age_average /= event.headcount
  event.headcount += unknowns
  event.save()

@permissions.is_logged_in
def star(request):
  if request.method == 'POST':
    token = request.POST.get('auth_token', None)
    user = models.TokenAuthModel.objects.filter(token=token).get().user
    event_id = request.POST.get('event_id', None)
    event = models.Event.objects.filter(id=event_id).get()
    stars = request.POST.get('stars', None)
    subscription = models.Subscription.objects.filter(user=user, event=event).get()
    subscription.stars = stars
    subscription.save()
    # recalculate event stars
    total = 0
    count = 0
    for s in models.Subscription.objects.filter(event=event).all():
      if (not s.stars):
        continue
      total += int(s.stars)
      count += 1
    event.stars = (total / count) if (count > 0) else 0
    event.save()
    return HttpResponse(simplejson.dumps({'empty': 'empty'}))
  return HttpResponseNotAllowed(['GET'])

@permissions.is_logged_in
def getUserStars(request):
  if request.method == 'POST':
    token = request.POST.get('auth_token', None)
    user = models.TokenAuthModel.objects.filter(token=token).get().user
    event_id = request.POST.get('event_id', None)
    event = models.Event.objects.filter(id=event_id).get()
    try:
      subscription = models.Subscription.objects.filter(user=user, event=event).get()
      return HttpResponse(simplejson.dumps({'stars': subscription.stars}))
    except models.Subscription.DoesNotExist:
      return HttpResponseBadRequest(simplejson.dumps({'error': 'Not checked in'}))
  return HttpResponseNotAllowed(['GET'])
