# Create your views here.
import string
import random
from django.http import HttpResponse
from django.http import HttpResponseNotAllowed,HttpResponseBadRequest,HttpResponseForbidden
from django.utils import simplejson
from django.contrib.auth.models import User
from api import models
import datetime
import logging
