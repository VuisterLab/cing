#!/usr/bin/env python
from __future__ import print_function, absolute_import

import subprocess
import os

from celery import Celery

try:
    import externalDataSources as edc
except ImportError:
    import cing.NRG.externalDataSources as edc


app = Celery('celeryShellCommandRunner',
             include=['cing.NRG.externalDataSources'],
             broker='amqp://guest@143.210.182.192//')

app.conf.update(
                CELERY_ACKS_LATE = True,
                CELERYD_PREFETCH_MULTIPLIER = 1,
                CELERYD_TASK_SOFT_TIME_LIMIT = 14400,
                CELERYD_TASK_TIME_LIMIT = 28800
               )


@app.task(name='cing.NRG.celeryShellCommandRunner')
def call_validateEntryPy_once(command):
    pdb = command.split()[2]
    logLocation = command.split()[4]

    p = os.path.join(logLocation, pdb[1:3], pdb)
    edc.ExternalDataSource._makePathIfNotExists( p )
    logLocation = os.path.join(p, pdb)
    with open('{}.out'.format(logLocation), 'w') as o, open('{}.err'.format(logLocation), 'w') as e:
        print('Calling: {}'.format(command))
        subprocess.call(['/bin/csh', '-c', command], stdout=o, stderr=e)