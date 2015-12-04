"""
WSGI config for vuisterSite project.

It exposes the WSGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/1.8/howto/deployment/wsgi/
"""
from __future__ import unicode_literals, absolute_import

import os
import subprocess

from django.core.wsgi import get_wsgi_application

try:
    from vuisterSite import localsettings
except ImportError:
    pass

def shell_source(script):
    pipe = subprocess.Popen('env'.format(script), stdout=subprocess.PIPE, shell=True, executable='/bin/bash')
    output = pipe.communicate()[0]
    priorEnvKeys = set(dict((line.split("=", 1) for line in output.splitlines())).keys())
    pipe = subprocess.Popen('source {}; env'.format(script), stdout=subprocess.PIPE, shell=True, executable='/bin/bash')
    output = pipe.communicate()[0]
    postEnv = dict((line.split("=", 1) for line in output.splitlines()))
    postEnvKeys = set(postEnv.keys())
    envKeys = priorEnvKeys ^ postEnvKeys
    return {k: postEnv[k] for k in envKeys}

cing_env = None
if 'CING_ENV_SETUP_SCRIPT' in os.environ:
    cing_env = shell_source(os.environ['CING_ENV_SETUP_SCRIPT'])
elif 'CINGROOT' in os.environ:
    setup_script = os.path.join(os.environ['CINGROOT'], 'python', 'cing', 'setupCingEnv.bash')
    if os.path.isfile(setup_script):
        cing_env = shell_source(setup_script)
if cing_env is not None:
    for k,v in cing_env.items():
        os.environ.setdefault(k,v)

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "vuisterSite.settings")
os.environ.setdefault('DJANGO_CONFIGURATION',  'Develop')
os.environ.setdefault('DJANGO_SECRET_KEY', '@0+9fi5b-(flog@1yadt-xb#k=xhonbv#&+3a7+ez-zj$=5jao')
os.environ.setdefault('ICING_DATA_DIRECTORY', '.')

application = get_wsgi_application()
