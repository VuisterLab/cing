from __future__ import unicode_literals, print_function, absolute_import, division

__author__ = 'TJ Ragan'

from .base import *

DEBUG = False

ALLOWED_HOSTS = ['www.icing.org.uk',
                 'icing.org.uk',
                 'www.nrgcing.org.uk',
                 'nrgcing.org.uk']

STATIC_ROOT = '/local/www/vuisterSite/static'

DATABASES = {
                'default': {
                    'ENGINE': 'django.db.backends.postgresql_psycopg2',
                    'NAME': 'icing',
                    'USER': 'icing',
                },
                'nrg': {
                    'ENGINE': 'django.db.backends.postgresql_psycopg2',
                    'NAME': 'pdbmlplus',
                    'USER': 'nrgcing1',
                    'PASSWORD': '4I4KMS'
                }
            }

os.environ.setdefault('ICING_DATA_DIRECTORY', os.path.join('/','local', 'iCingData'))
os.environ.setdefault('CINGROOT', os.path.join('/', 'local', 'cing'))