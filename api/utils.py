import string
import random

__author__ = 'schitic'

def tokenGenerator(size=16, chars=string.ascii_uppercase + string.digits):
  return ''.join(random.choice(chars) for x in range(size))
