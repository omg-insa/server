from api.models import BaseModel, ListModel
from core import logger
from django.test import TestCase
from django.contrib.auth.models import User
import datetime

class BaseModelTest(TestCase):

    def test_save(self):
      """
      Test if the base model can be saved
      """
      user = User(username='test@test.com')
      user.save()
      model_to_test = BaseModel()
      self.assertRaises(ValueError, model_to_test.save)
      has_error = False
      try:
        model_to_test.save(user=user)
      except ValueError:
        has_error = True
      self.assertFalse(has_error)
      self.assertEqual(BaseModel.objects.count(), 1)
      model_to_test.delete()
      self.assertEqual(BaseModel.objects.count(), 0)
      user.delete()

    def test_can_edit(self):
      """
      Test if the base model can be saved
      """
      user = User(username='test@test.com')
      user.save()
      model_to_test = BaseModel()
      model_to_test.save(user=user)
      user2 = User(username='test2@test.com')
      user2.save()
      has_error = False
      try:
        model_to_test.save(user=user2)
      except ValueError:
        has_error = True
      self.assertTrue(has_error)
      model_to_test.auth_users.add(user2)
      model_to_test.save(user=user)
      has_error = False
      try:
        model_to_test.save(user=user2)
      except ValueError:
        has_error = True
      self.assertFalse(has_error)
      model_to_test.auth_users.remove(user2)
      model_to_test.is_public = True
      model_to_test.save(user=user)
      has_error = False
      try:
        model_to_test.save(user=user2)
      except ValueError:
        has_error = True
      self.assertFalse(has_error)
      model_to_test.delete()
      user.delete()
      user2.delete()


class ListModelTest(TestCase):

  def test_add(self):
    """
    Test function for ListModel add function
    """
    model_to_test = ListModel()
    model_to_test.add(None)
    self.assertEqual(ListModel.objects.count(), 1)
    model_to_test.delete()
    model_to_test = ListModel()
    has_error = False
    message = ''
    try:
      model_to_test.add("String")
    except ValueError,e:
      has_error = True
      message = e.message
    self.assertTrue(has_error)
    self.assertEqual(message, 'The model must be saved before add')
    has_error = False
    message = ''
    user = User(username='test@test.com')
    user.save()
    model_to_test = ListModel()
    model_to_test.add(user)
    other_type = BaseModel()
    other_type.save(user=user)
    try:
      model_to_test.add(other_type);
    except ValueError,e:
      has_error = True
      message = e.message
    self.assertTrue(has_error)
    self.assertTrue(message, "Model type don't match")
    self.assertEqual(len(model_to_test.all()), 1)
    model_to_test.add(user)
    self.assertEqual(len(model_to_test.all()), 1)
    user.delete()
    other_type.delete()
    model_to_test.delete()

  def test_remove(self):
    """
    Test function for ListModel remove function
    """
    model_to_test = ListModel()
    user = User(username='test@test.com')
    user.save()
    user2 = User(username='test2@test.com')
    user2.save()
    model_to_test.add(user)
    model_to_test.add(user2)
    has_error = False
    message = ''
    try:
      model_to_test.remove("string")
    except ValueError,e:
      has_error = True
      message = e.message
    self.assertTrue(has_error)
    self.assertEqual(message, "The model must have an ID")
    has_error = False
    message = ''
    other_type = BaseModel()
    other_type.save(user=user)
    try:
      model_to_test.remove(other_type)
    except ValueError,e:
      has_error = True
      message = e.message
    self.assertTrue(has_error)
    self.assertEqual(message, "Model type don't match")
    self.assertEqual(len(model_to_test.all()), 2)
    model_to_test.remove(user)
    self.assertEqual(len(model_to_test.all()), 1)
    user.delete()
    user2.delete()
    other_type.delete()
    model_to_test.delete()