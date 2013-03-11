import datetime

from django.db import models
from django.contrib.auth.models import User

class DeviceInfo(models.Model):
  """Device information model"""
  device_type = models.CharField(max_length=100)
  device_manufacture = models.CharField(max_length=100)
  device_os = models.CharField(max_length=100)
  os_version = models.CharField(max_length=100)
  device_id = models.CharField(max_length=100)
  device_owner = models.ForeignKey(User, related_name='device_owner')

class Intrests(models.Model):
  name =  models.CharField(max_length=100)
  description =  models.CharField(max_length=100)

class UserIntrest(models.Model):
  intrest = models.ForeignKey(Intrests, related_name='user_intrest')
  user = models.ForeignKey(User, related_name='user_for_intresst')

class RecoveryTokens(models.Model):
  token  = models.CharField(max_length=100)
  user =  models.ForeignKey(User, related_name='for_who_must_recover')
  expiringDate =  models.DateTimeField()

class LocalPlaces(models.Model):
  name =  models.CharField(max_length=100)
  description =  models.CharField(max_length=10000)
  lon = models.CharField(max_length=100)
  lat = models.CharField(max_length=100)
  address = models.CharField(max_length=1000)
  type = models.CharField(max_length=100)

class TokenAuthModel(models.Model):
  """Auth token model for devices"""
  user = models.ForeignKey(User, related_name='token_username')
  device = models.ForeignKey(DeviceInfo, related_name='token_device_info')
  token = models.CharField(max_length=100)
  expiring_date = models.DateTimeField()

class ExtraInfoForUser(models.Model):
  user = models.ForeignKey(User, related_name='user_value')
  birthday  = models.CharField(max_length=100)
  sex = models.CharField(max_length=5)
  secret_question  = models.CharField(max_length=100)
  secret_answer  = models.CharField(max_length=100)
  status = models.CharField(max_length=100)

class Event(models.Model):
  place_id = models.CharField(max_length=100)
  local = models.CharField(max_length=100)
  name = models.CharField(max_length=100)
  date = models.DateField()
  start_time = models.CharField(max_length=100)
  end_time = models.CharField(max_length=100)
  headcount = models.CharField(max_length=100)
  description = models.CharField(max_length=100)
  age_average = models.CharField(max_length=100)
  price =  models.CharField(max_length=100)
  female_ratio = models.CharField(max_length=100)
  single_ratio =  models.CharField(max_length=100)
  status =  models.CharField(max_length=100)
  creator_id =  models.ForeignKey(User, related_name='event_createor')
  stars = models.CharField(max_length=100)

class EventIntrests(models.Model):
  event = models.ForeignKey(Event, related_name='event_intrest_ev')
  intrest = models.ForeignKey(Intrests, related_name='event_intrest_int')

class EventChatRoom(models.Model):
  event = models.ForeignKey(Event, related_name='event_chat_ev')
  message =  models.CharField(max_length=10000)
  user = models.ForeignKey(User, related_name='event_chat_user')
  date = models.DateTimeField()

class Subscription(models.Model):
  user = models.ForeignKey(User, related_name='subscriber')
  event = models.ForeignKey(Event, related_name='subscribed')
  stars = models.CharField(max_length=100)


class ListModel(models.Model):
  """Base model for lists."""
  object_type = models.CharField(max_length=100)
  objects_id = models.CharField(max_length=1000000000000)

  def all(self, *args, **kwargs):
    """Gets the list of objects."""
    list_to_return = []
    if not self.object_type:
      return list_to_return
    class_name = eval(self.object_type)
    if self.objects_id:
      for id in self.objects_id.split(';'):
        if id:
          list_to_return.append(class_name.objects.get(id=id))
    return list_to_return

  def add(self, object):
    """Adds an object to the list"""
    if not object:
      self.save()
      return
    if not hasattr(object, 'id') or not object.id:
      raise ValueError("The model must be saved before add")
    if not self.object_type:
      self.object_type = str(object._meta.object_name)
    elif str(object._meta.object_name) != self.object_type:
      raise ValueError("Model type don't match")
    if self.objects_id:
      already_objects = self.objects_id.split(';')
    else:
      already_objects = []
    if str(object.id) in already_objects:
      return
    already_objects.append(str(object.id))
    self.objects_id = self._convertListToString(already_objects)
    self.save()

  def remove(self, object):
    """Removes an object from the list."""
    if not hasattr(object, 'id') or not object.id:
      raise ValueError("The model must have an ID")
    if str(object._meta.object_name) != self.object_type:
      raise ValueError("Model type don't match")
    already_objects = self.objects_id.split(';')
    if str(object.id) in already_objects:
      already_objects.remove(str(object.id))
    self.objects_id = self._convertListToString(already_objects)
    self.save()

  def _convertListToString(self, list_of_objects):
    """Converts the list into a sting to be store into datastore."""
    return (';').join(list_of_objects)


class BaseModel(models.Model):
  """Base model that will be extended by all other models."""

  owner = models.ForeignKey(User, related_name='basemodel_owner')
  auth_users = models.ForeignKey(ListModel, null=True, related_name='basemodel_auth_users')
  is_public = models.BooleanField(default=False)
  last_updated_by = models.ForeignKey(User, related_name='basemodel_last_updated_by')
  last_updated_datetime = models.DateTimeField(auto_now_add=True)

  def __init__(self,*args, **kwargs):
    super(BaseModel, self).__init__(*args, **kwargs)

    for field in self._meta.fields:
      if type(field) == models.fields.related.ForeignKey:
        if field.rel.to == ListModel:
          if not eval('self.%s' % field.name):
            setattr(self, field.name, ListModel())

  def can_be_edited(self, user):
    """Function that will tell us if the user can edit or no the model."""
    return (self.is_public or user == self.owner or
            user in list(self.auth_users.all()))

  def save(self, *args, **kwargs):
    """Override for the save method to save last_updated_by. """
    user = kwargs.pop('user', None)
    if not user:
      raise ValueError("User not present in the model")
    if not hasattr(self, 'owner'):
      self.owner = user
    elif not self.can_be_edited(user):
      raise ValueError("User can't edit the model")
    self.last_updated_by = user
    self.last_updated_datetime = datetime.datetime.now()
    super(BaseModel, self).save(*args, **kwargs)

  def ToDict(self):
    """Converts the object to dictionary"""
    atributes_dictionary = {}
    for key, value in self.__dict__.iteritems():
      atributes_dictionary[key] = value
    return atributes_dictionary
