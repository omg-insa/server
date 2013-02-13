import re
import string
import random

__author__ = 'schitic'

def tokenGenerator(size=16, chars=string.ascii_uppercase + string.digits):
  return ''.join(random.choice(chars) for x in range(size))

def validateEmail(email):
  if len(email) > 3:
    if re.match("^.+\\@(\\[?)[a-zA-Z0-9\\-\\.]+\\.([a-zA-Z]{2,3}|[0-9]{1,3})(\\]?)$", email):
      return True
  return False