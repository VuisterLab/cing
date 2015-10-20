"""
WSGI config for vuisterSite project.

It exposes the WSGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/1.8/howto/deployment/wsgi/
"""
from __future__ import unicode_literals, absolute_import

import os
from vuisterSite import localsettings


from django.core.wsgi import get_wsgi_application

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "vuisterSite.settings")
os.environ.setdefault('DJANGO_CONFIGURATION',  'Develop')
os.environ.setdefault('DJANGO_SECRET_KEY', '@0+9fi5b-(flog@1yadt-xb#k=xhonbv#&+3a7+ez-zj$=5jao')
os.environ.setdefault('ICING_DATA_DIRECTORY', '.')

application = get_wsgi_application()
