from __future__ import unicode_literals, print_function, absolute_import, division

__author__ = 'TJ Ragan'


from .base import *


ALLOWED_HOSTS = []

DEBUG = True

EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend'

# INSTALLED_APPS += ('debug_toolbar',)

DATABASES = {
                'default': {
                    'ENGINE': 'django.db.backends.postgresql_psycopg2',
                    'HOST': '88.119.17.144',
                    'NAME': 'icing',
                    'USER': 'icing',
                },
                'nrg': {
                    'ENGINE': 'django.db.backends.postgresql_psycopg2',
                    'HOST': '88.119.17.144',
                    'NAME': 'pdbmlplus',
                    'USER': 'nrgcing1',
                    'PASSWORD': '4I4KMS'
                }
            }

os.environ.setdefault('ICING_DATA_DIRECTORY', os.path.join('/','Users', 'tjr22', 'Desktop', 'iCingData'))
os.environ.setdefault('CINGROOT', os.path.join('/Users', 'tjr22', 'Documents', 'CING', 'cing'))