from .base import *
from decouple import config


ALLOWED_HOSTS = [config("ALLOWED_HOSTS")]
